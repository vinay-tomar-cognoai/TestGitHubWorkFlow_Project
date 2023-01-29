"""
These are the HTMLs for creating the dynamic email UI. These variables is being used in utils_email_profile.py 
"""
from DeveloperConsoleApp.utils import get_developer_console_settings

developer_console_config = get_developer_console_settings()

LEGAL_NAME = 'AllinCall Research and Solutions Pvt. Ltd.'

if developer_console_config:
    LEGAL_NAME = developer_console_config.legal_name

EMAIL_HEAD = '\
<head>\
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
        font-family: "DM Sans";\
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
        font-family: "DM Sans";\
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
        font-family: "DM Sans";\
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
        font-family: "DM Sans";\
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
        font-family: "DM Sans", "Silka", -apple-system,\
                                  BlinkMacSystemFont, "Segoe UI", "Roboto",\
                                  "Oxygen", "Ubuntu", "Cantarell", "Fira Sans",\
                                  "Droid Sans", "Helvetica Neue", sans-serif;\
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
      .easychat-mailer-table-heading {\
        padding: 10px;\
        background: white;\
        color: #0036B5;\
        font-size: 14px;\
      }\
      .easychat-mailer-table {\
        border: none;\
        padding-top: 10px;\
        padding-bottom: 10px;\
        padding: 0;\
        width: 98%;\
        margin: 10px;\
        box-sizing: border-box;\
        background: #f9f9f9;\
        border: 1px solid #f7f7f7;\
        border-radius: 8px;\
      }\
      .easychat-mailer-table th {\
        border: none;\
        font-weight: 500;\
        text-align: left;\
        color: #4d4d4d;\
      }\
      .easychat-mailer-sub-heading {\
          color: #4d4d4d;\
          font-size: 14px;\
          font-weight: bold;\
          padding: 15px 6px;\
      }\
      .easychat-mailer-table tr td:not(.easychat-mailer-sub-heading) {\
          font-size: 13px;\
          color: #4d4d4d;\
          font-weight: normal;\
      }\
    .easychat-email-analytics-heading {\
            background: white;\
            border-bottom: 1px solid;\
        }\
        .easychat-email-analytics-heading td {\
            text-align: center;\
            color: #2d2d2d;\
            font-size: 16px;\
            font-weight: 600;\
            display: block;\
            justify-content: space-between;\
            margin: 20px 0px;\
            background: white;\
            border-bottom: 1px solid #e3e3e3;\
            padding-bottom: 30px;\
        }\
        .email-analytics-heading-p-first {\
            margin: 0;\
            width: 74%;\
            text-align: center;\
            padding-left: 13%;\
            display: inline;\
        }\
        .email-analytics-heading-p-last {\
            justify-self: flex-end;\
            float: right;\
            color: #565656;\
            font-size: 14px;\
            font-weight: normal;\
            margin: 0px 20px;\
        }\
        .easychat-mailer-download-reports-div {\
          background: #f6f6f6;\
          display: block;\
          margin: 10px;\
          border-radius: 8px;\
          padding: 20px 0px;\
          width: 98%;\
        }\
        .easychat-mailer-download-reports-p-head {\
          color: #5a5a5a;\
          font-size: 14px;\
          width: fit-content;\
          margin-left: 17%;\
        }\
        .easychat-mailer-download-reports-btn-div {\
          display: block;\
          margin-left: 3%;\
        }\
        .easychat-mailer-download-reports-btn {\
          text-decoration: none;\
          background: #154ECD;\
          color: white !important;\
          padding: 10px;\
          border-radius: 4px;\
          font-size: 14px;\
          margin: 0px 10px;\
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
        margin: 10px;\
        width: 98%;\
        height: auto;\
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
'


EMAIL_BODY_START = '<body>'


EMAIL_BODY_END = '</body>'


EMAIL_OUTER_TABLE_START = '\
<table width="80%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr" style="\
        background-color: rgb(242, 245, 247);\
        border-radius: 8px 8px 8px 8px;">\
        <tbody>\
'


EMAIL_OUTER_TABLE_END = '</tbody></table>'

EMAIL_COMPANY_LOGO = '\
    <tr>\
            <td align="center" valign="top" style="margin: 0; padding: 30px 15px 40px; background: linear-gradient(90deg,#0c75d6 0%, #1c35c7 100%,#1c35c7 100%); border-radius: 8px 8px 0 0;">\
            <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width: 700px;">\
                <tbody>\
                <tr>\
                    <td align="center" valign="center" style="margin: 0; padding: 0; border-radius: 30px;">\
                    <table align="center" border="0" cellpadding="0" cellspacing="0">\
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
                </tbody>\
            </table>\
            </td>\
        </tr>\
'


EMAIL_FOOTER = '\
    <tr style="background: linear-gradient(90deg,#0c75d6 0%, #1c35c7 100%,#1c35c7 100%);">\
            <td height="40"></td>\
        </tr>\
          <tr style="background: linear-gradient(90deg,#0c75d6 0%, #1c35c7 100%,#1c35c7 100%);">\
            <td align="center" style="padding: 0 0 11px 0;">\
              <table width="520" align="center" border="0" cellpadding="0" cellspacing="0" >\
                <tbody>\
                  <tr>\
                    <td align="center" valign="top" nowrap style="\
                          margin: 0px;\
                          padding: 0;\
                          font-size: 18px;\
                          line-height: 22px;\
                        ">\
                      <span style="\
                            color: #fff;\
                            font-size: 14px;\
                            white-space: nowrap;\
                          ">\
                        © Copyright 2021 ' + LEGAL_NAME + '\
                      </span>\
                    </td>\
                  </tr>\
                </tbody>\
              </table>\
            </td>\
          </tr>\
          <tr style="background: linear-gradient(90deg,#0c75d6 0%, #1c35c7 100%,#1c35c7 100%); border-radius: 0 0 8px 8px;">\
            <td align="center" style="padding-bottom: 85px;">\
              <table width="200" align="center" border="0" cellpadding="0" cellspacing="0">\
                <tbody>\
                  <tr>\
                    <td align="center" valign="top" nowrap style="\
                          margin: 0px;\
                          padding: 0 10px;\
                          font-size: 18px;\
                        ">\
                      <span style="\
                            color: #fff;\
                            font-size: 14px;\
                            white-space: nowrap;\
                          ">\
                        Visit our website to know more about us at:\
                      </span>\
                      <a href="https://www.getcogno.ai" style="\
                            color: #2e3233;\
                            font-weight: normal;\
                            text-decoration: none;\
                          ">\
                        <span style="\
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
                        ">\
                    </td>\
                  </tr>\
'


EMAIL_ANALYTICS_START = "\
    <tr class='easychat-email-analytics-heading'>\
        <td class='easychat-mailer-table-heading'>\
            <p class='email-analytics-heading-p-first'>Here's usage analytics for LiveChat </p>\
            <p class='email-analytics-heading-p-last'>()</p>\
        </td>\
    </tr>\
"

LIVECHAT_AGENT_CONNECTION_RATE = "\
    <tr class='easychat-email-agent-connection-rate'>\
        <td class='easychat-mailer-agent-connection-rate' style='text-align:center'>\
            <p class='email-analytics-agent-connection-rate-html' style='font-size:medium'>Agent connection rate is {} % </p>\
        </td>\
    </tr>\
"


EMAIL_TABLE_HEADING = '\
    <tr>\
        <td class="easychat-mailer-table-heading">\
            {}\
        </td>\
    </tr>\
'


EMAIL_TABLE_PARAMETERS_START = '\
    <tr style="background: white;">\
            <td align="left" valign="top">\
                <table class="td easychat-mailer-table" cellspacing="0" cellpadding="6">\
                    <thead>\
                        <tr>\
'


EMAIL_TABLE_PARAMETERS_HEAD = '\
    <th class="td" scope="col"">\
        {}\
    </th>\
'


EMAIL_TABLE_PARAMETERS_HEAD_END = '\
        </tr>\
    </thead>\
    <tbody>\
'

EMAIL_TABLE_SUB_HEADING = '\
    <tr>\
        <td class="easychat-mailer-sub-heading">{}</td>\
    </tr>\
'


EMAIL_TABLE_PARAMERTERS_TR_START = '<tr>'


EMAIL_TABLE_PARAMERTERS_VALUES = '<td>{}</td>'


EMAIL_TABLE_PARAMERTERS_TR_END = '</tr>'

EMAIL_TABLE_PARAMETERS_END = '\
    </tbody>\
    </table>\
    </tr>\
'

EMAIL_DOWNLOAD_REPORTS_START = '\
    <tr style="background: white;">\
          <td align="left" valign="top">\
            <div class="easychat-mailer-download-reports-div">\
            <div style="width: 100%;">\
              <p class="easychat-mailer-download-reports-p-head" style="margin-left: auto; margin-right:auto;">Download Reports</p>\
              <div class="easychat-mailer-download-reports-btn-div" style="text-align: center; margin-left: 0px !important; display: inline-block; width: 100%;">\
'


EMAIL_REPORT_BUTTON = '<a class="easychat-mailer-download-reports-btn" href="()" style="display: inline-block; margin-bottom: 10px !important;">Download {}</a>'


EMAIL_DOWNLOAD_REPORTS_END = '\
    </div>\
     </div>\
            </div>\
          </td>\
        </tr>\
'


EMAIL_DATE_ROW = '\
<tr style="background: white;">\
  <td style="color: #4d4d4d; font-size: 12px; padding: 0 10px 10px 10px;">\
    {}\
  </td>\
</tr>\
'
