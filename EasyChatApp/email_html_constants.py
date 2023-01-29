"""
These are the HTMLs for creating the dynamic email UI. These variables is being used in utils_email_configuration.py 
"""
from DeveloperConsoleApp.utils import get_developer_console_settings
from DeveloperConsoleApp.constants import GENERAL_LOGIN_LOGO
from django.conf import settings


def get_email_head_from_email_html_constant():

    config_obj = get_developer_console_settings()

    BRAND_LOGO = settings.EASYCHAT_HOST_URL + config_obj.login_logo

    if config_obj.login_logo == GENERAL_LOGIN_LOGO:
        BRAND_LOGO = "https://i.imgur.com/kwAv5nv.png"

    SECONDARY_COLOR = config_obj.secondary_color

    PRIMARY_COLOR = config_obj.primary_color

    EMAIL_HEAD = '<head>\
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
    <title>Cogno AI</title>\
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&display=swap" rel="stylesheet" />\
    <style type="text/css">\
      @media screen and (max-width: 600px),\
      screen and (max-device-width: 600px) {\
        body {\
          margin: 0 !important;\
          padding: 0 !important;\
        }\
        .heading {\
          margin: 10px !important;\
        }\
      }\
      @media screen and (-webkit-min-device-pixel-ratio: 0) and (max-width: 600px) {\
        body {\
          margin: 0 !important;\
          padding: 0 !important;\
        }\
      }\
      img{\
      max-width:600px;\
      }\
      @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap");\
      /* latin-ext */\
      @font-face {\
        font-family: \'DM Sans\';\
        font-style: normal;\
        font-weight: 400;\
        font-display: swap;\
        src: local("DM Sans Regular"), local("DMSans-Regular"),\
          url(https://fonts.gstatic.com/s/dmsans/v4/rP2Hp2ywxg089UriCZ2IHTWEBlwu8Q.woff2) format("woff2");\
        unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB,\
          U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;\
      }\
      /* latin */\
      @font-face {\
        font-family: \'DM Sans\';\
        font-style: normal;\
        font-weight: 400;\
        font-display: swap;\
        src: local("DM Sans Regular"), local("DMSans-Regular"),\
          url(https://fonts.gstatic.com/s/dmsans/v4/rP2Hp2ywxg089UriCZOIHTWEBlw.woff2) format("woff2");\
        unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,\
          U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,\
          U+2212, U+2215, U+FEFF, U+FFFD;\
      }\
      /* latin-ext */\
      @font-face {\
        font-family: \'DM Sans\';\
        font-style: normal;\
        font-weight: 700;\
        font-display: swap;\
        src: local("DM Sans Bold"), local("DMSans-Bold"),\
          url(https://fonts.gstatic.com/s/dmsans/v4/rP2Cp2ywxg089UriASitCBamC3YU-CnE6Q.woff2) format("woff2");\
        unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB,\
          U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;\
      }\
      /* latin */\
      @font-face {\
        font-family: \'DM Sans\';\
        font-style: normal;\
        font-weight: 700;\
        font-display: swap;\
        src: local("DM Sans Bold"), local("DMSans-Bold"),\
          url(https://fonts.gstatic.com/s/dmsans/v4/rP2Cp2ywxg089UriASitCBimC3YU-Ck.woff2) format("woff2");\
        unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,\
          U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,\
          U+2212, U+2215, U+FEFF, U+FFFD;\
      }\
      body,\
      table,\
      td,\
      tr,\
      span {\
        font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                  BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                  \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                  \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
      }\
      .flow-analytics{\
        border:1px solid #e5e5e5 !important;\
        padding-top:10px !important;\
        padding-bottom:10px !important;\
        width:80% !important;\
        color:#2e3233 !important;\
        font-size:18px !important;\
        word-wrap:break-word !important;\
        border-collapse:collapse !important;\
        margin-left:10% !important;\
      }\
    </style>\
  </head>\
  <body style="margin: 0; padding: 0; border: 0;">\
    <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr" style="\
          background-color: rgb(242, 245, 247);\
          background: #1c35c7;\
          background: linear-gradient(\
            90deg,\
            #' + PRIMARY_COLOR + ' 0%,\
            #' + SECONDARY_COLOR + ' 100%,\
            #' + SECONDARY_COLOR + ' 100%\
          );\
        ">\
      <tbody>\
        <tr>\
          <td align="center" valign="top" style="margin: 0; padding: 30px 15px 40px;">\
            <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width: 700px;">\
              <tbody>\
                <tr>\
                  <td align="center" valign="center" style="margin: 0; padding: 0; border-radius: 30px;">\
                    <table align="center" border="0" cellpadding="0" cellspacing="0" style="">\
                      <tbody>\
                        <tr>\
                          <td valign="top" align="center" style="padding: 0px; margin: 0px;">\
                            <img src="' + BRAND_LOGO + '" width="200" height="60" style="\
                                  border: none;\
                                  font-weight: bold;\
                                  height: auto;\
                                  line-height: 100%;\
                                  outline: none;\
                                  text-decoration: none;\
                                  text-transform: capitalize;\
                                  border-width: 0px;\
                                  border-style: none;\
                                  border-color: transparent;\
                                  font-size: 12px;\
                                  display: block;\
                                " />\
                          </td>\
                        </tr>\
                      </tbody>\
                    </table>\
                  </td>\
                </tr>\
                <tr>\
                  <td align="center" valign="top" height="30" style="margin: 0px; padding: 0;"></td>\
                </tr>\
                <tr>\
                  <td align="center" valign="top" style="margin: 0; padding: 0;">\
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%"\
                      style="max-width: 100%;">\
                      <tbody>\
                        <tr>\
                        </tr>\
                      </tbody>\
                    </table>\
                  </td>\
                </tr>\
                <tr>\
                  <td align="center" valign="top" style="margin: 0; padding: 0;">\
                    <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff"\
                      style="border-radius: 30px !important;">\
                      <tbody>\
                        <tr style="border-radius: 30px !important;">\
                          <td align="center" valign="top" style="\
                                margin: 0px;\
                                padding: 40px 60px 20px 60px;\
                                background-color: rgb(255, 255, 255);\
                                font-size: 18px;\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                  BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                  \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                  \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                line-height: 1.33;\
                                border-radius: 30px !important;\
                              " class="heading">\
                            <span style="\
                                  font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                  BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                  \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                  \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                  color: #181818;\
                                  font-size: 26px;\
                                ">\
                              <span style="font-weight: 700;">'
    return EMAIL_HEAD


EMAIL_ANALYTICS_DATE = '</span>\
                          </span>\
                        </td>\
                      </tr>\
                      <tr>\
                        <td align="left" class="em_font_16 em_gray" style="\
                            color: #000000;\
                            opacity: 0.55;\
                            text-align: left;\
                            font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                            font-size: 18px;\
                            line-height: 24px;\
                            padding-bottom: 6px;\
                            padding-left: 60px;\
                            border-collapse: collapse;\
                            mso-line-height-rule: exactly;\
                          ">\
                          <p style="\
                              color: #000000;\
                              opacity: 0.55;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              font-size: 16px;\
                              line-height: 24px;\
                              margin: 0px;\
                              padding: 0px 0px 0px 0px;\
                              font-style: normal;\
                            ">'
EMAIL_CATEGORY_START = '</p>\
                        </td>\
                      </tr>\
                      <tr>\
                        <td align="left" valign="top" style="\
                              margin: 0px;\
                              padding: 0 70px 40px 70px;\
                              background-color: rgb(255, 255, 255);\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 24px;\
                              border-bottom-left-radius: 30px;\
                              border-bottom-right-radius: 30px;\
                            ">\
                          <table class="td" cellspacing="0" cellpadding="6" border="1" style="\
                                border: 1px solid #e5e5e5;\
                                padding-top: 10px;\
                                padding-bottom: 10px;\
                                padding: 0;\
                                width: 100%;\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #2e3233;\
                                font-size: 18px;\
                                word-wrap: break-word;\
                                border-collapse: collapse;\
                              ">\
                            <thead>\
                              <tr>\
                                <th class="td" scope="col" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                      color: #2e3233;\
                                    ">\
                                  Channel\
                                </th>'


EMAIL_CATEGORY_HTML = '<th class="td" scope="col" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">'

EMAIL_ANALYTICS_BODY = '<tbody>\
                              <tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Total Messages\
                                </td>'


EMAIL_ANLYTICS_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'


EMAIL_ACCURACY_START = '</p>\
                        </td>\
                      </tr>\
                      <tr>\
                        <td align="left" valign="top" style="\
                              margin: 0px;\
                              padding: 0 60px 40px 60px;\
                              background-color: rgb(255, 255, 255);\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 24px;\
                              border-bottom-left-radius: 30px;\
                              border-bottom-right-radius: 30px;\
                            ">\
                          <table class="td" cellspacing="0" cellpadding="6" border="1" style="\
                                border: 1px solid #e5e5e5;\
                                padding-top: 10px;\
                                padding-bottom: 10px;\
                                padding: 0;\
                                width: 100%;\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #2e3233;\
                                font-size: 18px;\
                                word-wrap: break-word;\
                                border-collapse: collapse;\
                              "><tbody>'


EMAIL_ACCURACY_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Accuracy\
                                </td>'


EMAIL_ACCURACY_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'


EMAIL_IDENTIFIED_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Identified Messages\
                                </td>'

EMAIL_IDENTIFIED_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'


EMAIL_UNIDENTIFIED_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Unidentified Messages\
                                </td>'

EMAIL_UNDENTIFIED_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                     font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'

EMAIL_TOTAL_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Total Queries\
                                </td>'

EMAIL_TOTAL_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: center;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'

EMAIL_UNANSWERED_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Unanswered Queries\
                                </td>'

EMAIL_UNANSWERED_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: center;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'

EMAIL_BOT_ACCURACY_VALUES = '<td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: center;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  <span class="woocommerce-Price-amount amount">'


EMAIL_MTD_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  MTD Sessions\
                                </td>'

EMAIL_YTD_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  YTD Sessions\
                                </td>'


EMAIL_FORM_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Form Assist Analytics\
                                </td>'

EMAIL_FORM_UNIQUE_BODY = '<tr class="table_item">\
                                <td class="td" style="\
                                      border: 1px solid #e5e5e5;\
                                      padding-top: 10px;\
                                      padding-bottom: 10px;\
                                      text-align: left;\
                                      vertical-align: middle;\
                                      color: #2e3233;\
                                      font-size: 18px;\
                                      word-wrap: break-word;\
                                      border-collapse: collapse;\
                                      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    ">\
                                  Form Assist Unique Users\
                                </td>'

EMAIL_FILE_BODY = '<tr><table role="presentation" width="252" border="0" cellspacing="0" cellpadding="0"\
                            align="center" style="\
                                width: 200px;\
                                min-width: 200px;\
                                border-radius: 90px;\
                                margin: 15px auto;\
                                border-collapse: collapse;\
                                mso-table-lspace: 0px;\
                                mso-table-rspace: 0px;\
                              " bgcolor="#2743CB">\
                            <tr>\
                              <td align="center" valign="middle" class="em_bold" height="40" style="\
                                    height: 40px;\
                                    color: #ffffff;\
                                    font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                    font-size: 16px;\
                                    font-weight: 400;\
                                    border-collapse: collapse;\
                                    mso-line-height-rule: exactly;\
                                    border-radius: 20px !important;\
                                  ">'

EMAIL_FOOTER = '<span style="\
                               font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #828282;\
                                font-size: 16px;\
                              ">\
                            <p style="margin-left:20px;margin-right:20px;">'

EMAIL_BODY_END = '</p>\
                          </span>\
                        </td>\
                      </tr>\
                    </tbody>\
                  </table>\
                </td>\
              </tr>\
              <tr>\
                <td height="40"></td>\
              </tr>\
              <tr>\
                <td align="center" style="padding: 0 0 11px 0;">\
                  <table width="520" align="center" border="0" cellpadding="0" cellspacing="0">\
                    <tbody>\
                      <tr>\
                        <td align="center" valign="top" nowrap style="\
                              margin: 0px;\
                              padding: 0;\
                              font-size: 18px;\
                            font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 22px;\
                            ">\
                          <span style="\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #fff;\
                                font-size: 14px;\
                                white-space: nowrap;\
                              ">\
                            © Copyright 2021 AllinCall Research and Solutions Pvt. Ltd.\
                          </span>\
                        </td>\
                      </tr>\
                    </tbody>\
                  </table>\
                </td>\
              </tr>\
              <tr>\
                <td align="center" style="padding-bottom: 85px;">\
                  <table width="200" align="center" border="0" cellpadding="0" cellspacing="0">\
                    <tbody>\
                      <tr>\
                        <td align="center" valign="top" nowrap style="\
                              margin: 0px;\
                              padding: 0 10px;\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                            ">\
                          <a href="https://www.getcogno.ai" style="\
                                color: #2e3233;\
                                font-weight: normal;\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                text-decoration: none;\
                              ">\
                            <span style="\
                                  font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                  color: #fff;\
                                  font-size: 14px;\
                                  white-space: nowrap;\
                                  border-bottom: 1px solid #fff;\
                                  line-height: 22px;\
                                ">Visit getcogno.ai</span>\
                          </a>\
                        </td>\
                        <td align="center" valign="top" nowrap style="\
                              margin: 0px;\
                              padding: 0 10px;\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                            ">\
                        </td>\
                      </tr>\
                    </tbody>\
                  </table>\
                </td>\
              </tr>\
            </tbody>\
          </table>\
        </td>\
      </tr>\
    </tbody>\
  </table>\
</body>'


FLOW_ANALYTICS_HEADER = '<tr><table class="flow-analytics" role="flow-analytics" id="flow-analytics" cellspacing="0" cellpadding="6" border="1"><thead><tr><th scope="col" style="border:1px solid #e5e5e5;padding-top:10px;padding-bottom:10px;text-align:left;font-family:"DM Sans","Silka",-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Oxygen","Ubuntu","Cantarell","Fira Sans","Droid Sans","Helvetica Neue",sans-serif;color:#2e3233">Intent</th><th scope="col" style="border:1px solid #e5e5e5;padding-top:10px;padding-bottom:10px;text-align:left;font-family:"DM Sans","Silka",-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Oxygen","Ubuntu","Cantarell","Fira Sans","Droid Sans","Helvetica Neue",sans-serif;color:#2e3233">Intent Trigger Count</th><th scope="col" style="border:1px solid #e5e5e5;padding-top:10px;padding-bottom:10px;text-align:left;font-family:"DM Sans","Silka",-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Oxygen","Ubuntu","Cantarell","Fira Sans","Droid Sans","Helvetica Neue",sans-serif;color:#2e3233">Flow Completion Count</th><th scope="col" style="border:1px solid #e5e5e5;padding-top:10px;padding-bottom:10px;text-align:left;font-family:"DM Sans","Silka",-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Oxygen","Ubuntu","Cantarell","Fira Sans","Droid Sans","Helvetica Neue",sans-serif;color:#2e3233">Channel</th></tr></thead><tbody>'
FLOW_ANALYTICS_ROW = '<td style="border:1px solid #e5e5e5;padding-top:10px;padding-bottom:10px;text-align:left;vertical-align:middle;color:#2e3233;font-size:18px;word-wrap:break-word;border-collapse:collapse;font-family:"DM Sans","Silka",-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Oxygen","Ubuntu","Cantarell","Fira Sans","Droid Sans","Helvetica Neue",sans-serif">'


EMAIL_FILE_BODY_SIGNUP = '<table>'

EMAIL_DAILY_MAIL_HEAD = '<head>\
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
  <title>Cogno AI</title>\
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&display=swap" rel="stylesheet" />\
  <style type="text/css">\
    @media screen and (max-width: 600px),\
    screen and (max-device-width: 600px) {\
      body {\
        margin: 0 !important;\
        padding: 0 !important;\
      }\
      .heading {\
        margin: 10px !important;\
      }\
    }\
    @media screen and (-webkit-min-device-pixel-ratio: 0) and (max-width: 600px) {\
      body {\
        margin: 0 !important;\
        padding: 0 !important;\
      }\
    }\
    img{\
    max-width:350px;\
    }\
    @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap");\
    /* latin-ext */\
    @font-face {\
      font-family: \'DM Sans\';\
      font-style: normal;\
      font-weight: 400;\
      font-display: swap;\
      src: local("DM Sans Regular"), local("DMSans-Regular"),\
        url(https://fonts.gstatic.com/s/dmsans/v4/rP2Hp2ywxg089UriCZ2IHTWEBlwu8Q.woff2) format("woff2");\
      unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB,\
        U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;\
    }\
    /* latin */\
    @font-face {\
      font-family: \'DM Sans\';\
      font-style: normal;\
      font-weight: 400;\
      font-display: swap;\
      src: local("DM Sans Regular"), local("DMSans-Regular"),\
        url(https://fonts.gstatic.com/s/dmsans/v4/rP2Hp2ywxg089UriCZOIHTWEBlw.woff2) format("woff2");\
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,\
        U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,\
        U+2212, U+2215, U+FEFF, U+FFFD;\
    }\
    /* latin-ext */\
    @font-face {\
      font-family: \'DM Sans\';\
      font-style: normal;\
      font-weight: 700;\
      font-display: swap;\
      src: local("DM Sans Bold"), local("DMSans-Bold"),\
        url(https://fonts.gstatic.com/s/dmsans/v4/rP2Cp2ywxg089UriASitCBamC3YU-CnE6Q.woff2) format("woff2");\
      unicode-range: U+0100-024F, U+0259, U+1E00-1EFF, U+2020, U+20A0-20AB,\
        U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;\
    }\
    /* latin */\
    @font-face {\
      font-family: \'DM Sans\';\
      font-style: normal;\
      font-weight: 700;\
      font-display: swap;\
      src: local("DM Sans Bold"), local("DMSans-Bold"),\
        url(https://fonts.gstatic.com/s/dmsans/v4/rP2Cp2ywxg089UriASitCBimC3YU-Ck.woff2) format("woff2");\
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,\
        U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,\
        U+2212, U+2215, U+FEFF, U+FFFD;\
    }\
    body,\
    table,\
    td,\
    tr,\
    span {\
      font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
    }\
    .flow-analytics{\
      border:1px solid #e5e5e5 !important;\
      padding-top:10px !important;\
      padding-bottom:10px !important;\
      width:80% !important;\
      color:#2e3233 !important;\
      font-size:18px !important;\
      word-wrap:break-word !important;\
      border-collapse:collapse !important;\
      margin-left:10% !important;\
    }\
       .dot{\
      height: 14px;\
      width: 14px;\
      background-color: #2697FF;\
      border-radius: 50%;\
      display: inline-block;\
      margin-right: 8px !important;\
      margin:auto;\
    }\
    .chip{\
    display: inline-flex;\
    padding: 0 12px;\
    text-align: center;\
    align-items: center;\
    height: 40px;\
    font-size: 13px;\
    border-radius: 5px;\
    margin: 5px;\
    }\
    .chips-wrapper{\
        margin: auto;\
    }\
    .chip-label{\
        margin: auto;\
    }\
    .chart-container{\
        display: flex;\
        background: #f9f9f9;\
        border-radius: 12px;\
        margin: auto;\
        width: 90%;\
        height: auto;\
        padding:16px;\
        margin-bottom: 20px;\
    }\
    .img-container{\
        display: flex;\
        align-items: center;\
        margin: auto;\
    }\
    .img-container-line-chart img{\
      max-width:100% !important;\
    }\
  </style>\
</head>\
<body style="margin: 0; padding: 0; border: 0;">\
  <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr" style="\
        background-color: rgb(242, 245, 247);\
        background: #1c35c7;\
        background: linear-gradient(\
          90deg,\
          #0c75d6 0%,\
          #1c35c7 100%,\
          #1c35c7 100%\
        );\
      ">\
    <tbody>\
      <tr>\
        <td align="center" valign="top" style="margin: 0; padding: 30px 15px 40px;">\
          <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width: 700px;">\
            <tbody>\
              <tr>\
                <td align="center" valign="center" style="margin: 0; padding: 0; border-radius: 30px;">\
                  <table align="center" border="0" cellpadding="0" cellspacing="0" style="">\
                    <tbody>\
                      <tr>\
                        <td valign="top" align="center" style="padding: 0px; margin: 0px;">\
                          <img src="https://i.imgur.com/kwAv5nv.png" width="200" height="60" style="\
                                border: none;\
                                font-weight: bold;\
                                height: auto;\
                                line-height: 100%;\
                                outline: none;\
                                text-decoration: none;\
                                text-transform: capitalize;\
                                border-width: 0px;\
                                border-style: none;\
                                border-color: transparent;\
                                font-size: 12px;\
                                display: block;\
                              " />\
                        </td>\
                      </tr>\
                    </tbody>\
                  </table>\
                </td>\
              </tr>\
              <tr>\
                <td align="center" valign="top" height="30" style="margin: 0px; padding: 0;"></td>\
              </tr>\
              <tr>\
                <td align="center" valign="top" style="margin: 0; padding: 0;">\
                  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%"\
                    style="max-width: 100%;">\
                    <tbody>\
                      <tr>\
                      </tr>\
                    </tbody>\
                  </table>\
                </td>\
              </tr>\
              <tr>\
                <td align="center" valign="top" style="margin: 0; padding: 0;">\
                  <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff"\
                    style="border-radius: 30px !important;">\
                    <tbody>\
                      <tr style="border-radius: 30px !important;">\
                        <td align="center" valign="top" style="\
                              margin: 0px;\
                              padding: 40px 60px 20px 60px;\
                              background-color: rgb(255, 255, 255);\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 1.33;\
                              border-radius: 30px !important;\
                            " class="heading">\
                          <span style="\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #181818;\
                                font-size: 26px;\
                              ">\
                            <span style="font-weight: 700;color:#121212 !important;">'

EMAIL_HEADING_END = '</span>\
                          </span>\
                        </td>\
                      </tr>'
EMAIL_ANALYTICS_CHART_HEADING = '<tr style="border-radius: 30px !important;">\
                        <td align="center" valign="top" style="\
                              margin: 0px;\
                              padding: 40px 60px 20px 60px;\
                              background-color: rgb(255, 255, 255);\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 1.33;\
                              border-radius: 30px !important;\
                            " class="heading">\
                          <span style="\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #181818;\
                                font-size: 16px;\
                              ">\
                            <span style="font-weight: 500;">'

EMAIL_DAILY_ANALYTICS_DATE = '<tr>\
                        <td align="left" class="em_font_16 em_gray" style="\
                            color: #000000;\
                            opacity: 0.55;\
                            text-align: left;\
                            font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                            font-size: 18px;\
                            line-height: 24px;\
                            padding-bottom: 6px;\
                            padding-left: 70px;\
                            border-collapse: collapse;\
                            mso-line-height-rule: exactly;\
                          ">\
                          <p style="\
                              color: #000000;\
                              opacity: 0.55;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              font-size: 16px;\
                              line-height: 24px;\
                              margin: 0px;\
                              padding: 0px 0px 0px 0px;\
                              font-style: normal;\
                            ">'
EMAIL_DAILY_BOT_USAGE_ANLAYTICS_HEADING_START = '<tr style="border-radius: 30px !important;">\
                        <td align="center" valign="top" style="\
                              margin: 0px;\
                              padding: 40px 60px 20px 60px;\
                              background-color: rgb(255, 255, 255);\
                              font-size: 18px;\
                              font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                              line-height: 1.33;\
                              border-radius: 30px !important;\
                            " class="heading">\
                          <span style="\
                                font-family: \'DM Sans\', \'Silka\', -apple-system,\
                                BlinkMacSystemFont, \'Segoe UI\', \'Roboto\',\
                                \'Oxygen\', \'Ubuntu\', \'Cantarell\', \'Fira Sans\',\
                                \'Droid Sans\', \'Helvetica Neue\', sans-serif;\
                                color: #181818;\
                                font-size: 26px;\
                              ">\
                            <span style="font-weight: 700;color:#121212 !important;">'

EMAIL_ANALYTICS_END_LINE = "<tr><hr style='border:0.5px solid #E3E3E3;margin-bottom: 15px;margin-top: 35px;'></tr>"
