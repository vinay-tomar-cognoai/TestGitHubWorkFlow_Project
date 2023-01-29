from django.core.validators import URLValidator as url_validator
from django.core.exceptions import ValidationError
from django.conf import settings

import re
import logging

logger = logging.getLogger(__name__)

ASK_FOR_SIGNIN_GOOGLE = {
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
                            "textToSpeech": "To use this service, please link your account",
                            "displayText": "To use this service, please link your account"
                        }
                    },
                ],
            },
            "systemIntent": {
                "intent": "actions.intent.SIGN_IN",
                "data": {
                    "@type": "type.googleapis.com/google.actions.v2.SignInValueSpec"
                }
            }
        }
    }
}

"""
Sample table card response

DEFAULT_TABLE_CARD = {
    "tableCard": {
        "rows": [
            {
              "cells": [
                    {
                      "text": "row 1 item 1"
                    },
                    {
                      "text": "row 1 item 2"
                    },
                    {
                      "text": "row 1 item 3"
                    }
                ],
                "dividerAfter": True
            },
            {
              "cells": [
                    {
                        "text": "row 2 item 1"
                    },
                    {
                        "text": "row 2 item 2"
                    },
                    {
                        "text": "row 2 item 3"
                    }
                ],
                "dividerAfter": True
            }
        ],
        "columnProperties": [
            {
                "header": "header 1"
            },
            {
                "header": "header 2"
            },
            {
                "header": "header 3"
            }
        ]
    }
}
"""


"""
function: build_google_home_table_card_response
input params:
    table_list:list of table card details

builds table card response for google assistant according to template
"""


def build_google_home_table_card_response(table_list):

    if len(table_list) <= 1:
        return None

    column_properties = []
    for header in table_list[0]:
        column_properties.append({
            "header": header
        })

    table_card_json = {
        "tableCard": {
            "rows": [],
            "columnProperties": column_properties
        }
    }

    no_rows = len(table_list)
    for iterator in range(1, no_rows):
        row_json = {
            "cells": [],
            "dividerAfter": True
        }
        for inner in range(len(table_list[iterator])):
            row_json["cells"].append({
                "text": table_list[iterator][inner]
            })
        table_card_json["tableCard"]["rows"].append(row_json)

    return table_card_json


"""
Sample text speech response
{
    "simpleResponse": {
      "textToSpeech": "Howdy, this is GeekNum. I can tell you fun facts about almost any number, my favorite is 42. What number do you have in mind?",
      "displayText": "Howdy! I can tell you fun facts about almost any number. What do you have in mind?"
    }
}
"""


"""
function: html_parser_for_google_response
input params:
    raw_html: raw HTML content

returns html free text
"""


def html_parser_for_google_response(raw_html):
    raw_html = raw_html.replace("<br>", "\n")
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


"""
function: build_google_home_text_speech_response
input params:
    text: text response
    speech: speech response

builds simple response for google assistant according to template
"""


def build_google_home_text_speech_response(text, speech):
    text = str(text)
    text = html_parser_for_google_response(text)
    speech = html_parser_for_google_response(speech)

    return {
        "simpleResponse": {
            "textToSpeech": str(speech),
            "displayText": str(text)
        }
    }


"""
"suggestions": [
  {
    "title": "Suggestion Chips"
  },
  {
    "title": "suggestion 1"
  },
  {
    "title": "suggestion 2"
  }
]
"""


"""
function: build_google_home_suggestion_chips
input params:
    title_list: list of title of suggection

builds suggestion chips response for google assistant according to template
"""


def build_google_home_suggestion_chips(title_list):
    if len(title_list) <= 1:
        return None

    suggestion_chips = []
    for title in title_list:
        suggestion_chips.append({
            "title": str(title)
        })
    return suggestion_chips


"""
Visual selection responses

Sample List select

"systemIntent": {
        "intent": "actions.intent.OPTION",
        "data": {
          "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
          "listSelect": {
            "title": "List Title",
            "items": [
              {
                "optionInfo": {
                  "key": "SELECTION_KEY_ONE",
                  "synonyms": [
                    "synonym 1",
                    "synonym 2",
                    "synonym 3"
                  ]
                },
                "description": "This is a description of a list item.",
                "image": {
                  "url": "IMG_URL_AOG.com",
                  "accessibilityText": "Image alternate text"
                },
                "title": "Title of First List Item"
              },
              {
                "optionInfo": {
                  "key": "SELECTION_KEY_GOOGLE_HOME",
                  "synonyms": [
                    "Google Home Assistant",
                    "Assistant on the Google Home"
                  ]
                },
                "description": "Google Home is a voice-activated speaker powered by the Google Assistant.",
                "image": {
                  "url": "IMG_URL_GOOGLE_HOME.com",
                  "accessibilityText": "Google Home"
                },
                "title": "Google Home"
              },
              {
                "optionInfo": {
                  "key": "SELECTION_KEY_GOOGLE_PIXEL",
                  "synonyms": [
                    "Google Pixel XL",
                    "Pixel",
                    "Pixel XL"
                  ]
                },
                "description": "Pixel. Phone by Google.",
                "image": {
                  "url": "IMG_URL_GOOGLE_PIXEL.com",
                  "accessibilityText": "Google Pixel"
                },
                "title": "Google Pixel"
              }
            ]
          }
        }
      }
"""


"""
function: build_google_home_visual_selection_list_select
input params:
    selection_list: list of recommedation
builds recommedation response for google assistant according to template
"""


def build_google_home_visual_selection_list_select(selection_list):

    if len(selection_list) <= 1:
        return None

    DEFAULT_WEBHOOK_SYSTEM_INTENT = {  # noqa: N806
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

    for selection in selection_list:
        key = selection["key"]
        value = selection["value"]

        option_info = {
            "optionInfo": {
                "key": key
            },
            "title": value
        }

        if "image" in selection:
            option_info["image"] = {
                "url": selection["image"]["url"],
                "accessibilityText": selection["image"]["accessibilityText"]
            }

        DEFAULT_WEBHOOK_SYSTEM_INTENT["systemIntent"]["data"]["listSelect"]["items"].append(
            option_info)

    return DEFAULT_WEBHOOK_SYSTEM_INTENT


"""
basicCard

{
    "basicCard": {
      "title": "Title: this is a title",
      "subtitle": "This is a subtitle",
      "formattedText": "This is a basic card.",
      "image": {
        "url": "https://example.com/image.png",
        "accessibilityText": "Image alternate text"
      },
      "buttons": [
        {
          "title": "This is a button",
          "openUrlAction": {
            "url": "https://assistant.google.com/"
          }
        }
      ],
      "imageDisplayOptions": "CROPPED"
    }
}

"""


def easychat_url_validator(url):
    remote_url = url
    try:
        url_validator(remote_url)
    except ValidationError as e:
        logger.error("easychat_url_validator: %s", e, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        remote_url = settings.EASYCHAT_HOST_URL + remote_url
        try:
            url_validator(remote_url)
        except ValidationError as e:
            logger.error("easychat_url_validator: check 2: %s", e, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return None
    return remote_url


"""
function: build_google_home_basic_card_response
input params:
    basic_card: json containing card details
builds basic card response for google assistant according to template
"""


def build_google_home_basic_card_response(basic_card):

    if "title" not in basic_card:
        return None

    if "image_url" not in basic_card:
        return None

    if "image_accessibility_text" not in basic_card:
        return None

    image_url = basic_card["image_url"]
    image_url = easychat_url_validator(image_url)

    if image_url == None:
        return None

    DEFAULT_BASIC_CARD = {  # noqa: N806
        "basicCard": {
            "title": str(basic_card["title"]),
            "image": {
                "url": str(image_url),
                "accessibilityText": str(basic_card["image_accessibility_text"])
            },
            "imageDisplayOptions": "CROPPED"
        }
    }

    if "description" in basic_card:
        DEFAULT_BASIC_CARD["basicCard"][
            "formattedText"] = basic_card["description"]

    if "button_title" in basic_card and "button_url" in basic_card:

        button_url = basic_card["button_url"]
        button_url = easychat_url_validator(button_url)

        if button_url == None:
            return None

        DEFAULT_BASIC_CARD["basicCard"]["buttons"] = [{
            "title": str(basic_card["button_title"]),
            "openUrlAction": {
                "url": str(button_url)
            }
        }]

    return DEFAULT_BASIC_CARD


"""
Google Home carouselBrowse

sample carouselBrowse

{
"carouselBrowse": {
  "items": [
    {
      "title": "Title of item 1",
      "openUrlAction": {
        "url": "google.com"
      },
      "description": "Description of item 1",
      "footer": "Item 1 footer",
      "image": {
        "url": "IMG_URL.com",
        "accessibilityText": "Image alternate text"
      }
    },
    {
      "title": "Google Assistant",
      "openUrlAction": {
        "url": "google.com"
      },
      "description": "Google Assistant on Android and iOS",
      "footer": "More information about the Google Assistant",
      "image": {
        "url": "IMG_URL_Assistant.com",
        "accessibilityText": "Image alternate text"
      }
    }
  ]
}
}

"""


"""
function: build_google_home_carousel_browse_response
input params:
    carousel_tiles: list of carousel card tiles
builds carousel tiles response for google assistant according to template
"""


def build_google_home_carousel_browse_response(carousel_tiles):

    if len(carousel_tiles) < 2 or len(carousel_tiles) > 10:
        return None

    DEFAULT_CAROUSEL_BROWSE = {  # noqa: N806
        "carouselBrowse": {
            "items": []
        }
    }

    for carousel_tile in carousel_tiles:

        if "title" not in carousel_tile:
            return None

        if "target_url" not in carousel_tile:
            return None

        if "image_url" not in carousel_tile:
            return None

        if "image_accessibility_text" not in carousel_tile:
            return None

        target_url = carousel_tile["target_url"]
        target_url = easychat_url_validator(target_url)

        if target_url == None:
            return None

        image_url = carousel_tile["image_url"]
        image_url = easychat_url_validator(image_url)

        if image_url == None:
            return None

        tile_json = {
            "title": str(carousel_tile["title"].encode("ascii", errors="ignore").decode("ascii")),
            "openUrlAction": {
                "url": str(target_url)
            },
            "image": {
                "url": str(image_url),
                "accessibilityText": str(carousel_tile["image_accessibility_text"].encode("ascii", errors="ignore").decode("ascii"))
            }
        }

        DEFAULT_CAROUSEL_BROWSE["carouselBrowse"]["items"].append(
            tile_json)

    return DEFAULT_CAROUSEL_BROWSE
