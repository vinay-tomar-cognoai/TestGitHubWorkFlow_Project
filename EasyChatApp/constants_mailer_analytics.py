DEFAULT_MAIL_SUBJECT = "COGNO AI - ChatBot Report Mailer"

DEFAULT_TIME_INTERVAL_GRAPH = 7

FLOW_COMPLETION_CHOICES = (
    ("1", "Select All"),
    ("2", "Select Top 5 only"),
)

INTENT_ANALYTICS_CHOICES = (
    ("1", "Select All"),
    ("2", "Select Top 5 only"),
)

TRAFFIC_ANALYTICS_CHOICES = (
    ("1", "Select All"),
    ("2", "Select Top 5 (based on Sources)"),
    ("3", "Select Top 5 (based on Bot Views)"),
    ("4", "Select Top 5 (based on Avg. Time on the Bot)"),
)

MESSAGE_ANALYTICS_PARAMETERS = {
    "total_messages": 1,
    "identified_messages": 2,
    "unidentified_messages": 3,
    "positive_feedback": 4,
    "negative_feedback": 5,
    "bot_accuracy": 6,
    "intuitive_messages": 7,
}

SESSION_ANALYTICS_PARAMETERS = {
    "total_sessions": 1,
    "avg_session_duration": 2,
    "avg_messages_in_session": 3,
    "total_session_duration": 4,
    "total_bot_clicks": 5,
}

USER_ANALYTICS_PARAMETERS = {
    "total_users": 1,
    "form_filled": 2,
    "authentication_failure": 3,
    "authentication_successful": 4,
    "customer_initiated_conversation": 5,
    "business_initiated_conversation": 6,
}

LIVECHAT_ANALYTICS_PARAMETERS = {
    "intent_called": 1,
    "conversion_percent": 2,
    "agent_connected": 3,
    "request_raised": 4,
}

DEFAULT_TRAFFIC_ANALYTICS_PARAMETERS = [
    'select_all',
    'select_top_five_based_sources',
    'select_top_five_based_bot_views',
    'select_top_five_based_avg_time',
]

MESSAGE_ANALYTICS_MAP = {
    "total_messages": "Total Messages",
    "identified_messages": "Identified Messages",
    "unidentified_messages": "Unidentified Messages",
    "intuitive_messages": "Intuitive Messages",
    "negative_feedback": "Messages with -ve Feedback",
    "positive_feedback": "Messages with +ve Feedback",
    "bot_accuracy": "Accuracy %",
}

SESSION_ANALYTICS_MAP = {
    "total_sessions": "No. of unique Sessions",
    "avg_session_duration": "Average Session Duration",
    "avg_messages_in_session": "Average No. of Messages per Session",
    "total_session_duration": "Total Session Duration",
    "total_bot_clicks": "No. of clicks on bot"
}

USER_ANALYTICS_MAP = {
    "total_users": "Total Users",
    "form_filled": "Form Filled",
    "authentication_failure": "Authentication Failure",
    "authentication_successful": "Authentication Successful",
    "customer_initiated_conversation": "Customer Initiated Conversation",
    "business_initiated_conversation": "Business Initiated Conversation"
}

LIVECHAT_ANALYTICS_MAP = {
    "intent_called": "Chat with an expert",
    "conversion_percent": "Conversion",
    "agent_connected": "Agent Connected",
    "request_raised": "Request Raised"
}

DOWNLOAD_REPORTS_MAP = {
    "bot_queries": "Bot Queries",
    "unanswered": "Unanswered",
    "intuitive": "Intuitive",
    "dropoff": "User Specific Dropoff",
    "language_analytics": "Language based analytics",
    "csat_data": "CSAT Report",
}

"""
Sample Data for Analytics Sample Mail
"""

MESSAGE_ANALYTICS_DATA = {
    "total_messages": {
        "Daily": "9",
        "MTD": "33",
        "WTD": "22",
        "YTD": "102",
        "LMSD": "12"
    },
    "identified_messages": {
        "Daily": "8",
        "MTD": "28",
        "WTD": "20",
        "YTD": "90",
        "LMSD": "11"
    },
    "unidentified_messages": {
        "Daily": "1",
        "MTD": "5",
        "WTD": "2",
        "YTD": "12",
        "LMSD": "1"
    },
    "intuitive_messages": {
        "Daily": "3",
        "MTD": "10",
        "WTD": "5",
        "YTD": "50",
        "LMSD": "13"
    },
    "negative_feedback": {
        "Daily": "2",
        "MTD": "3",
        "WTD": "2",
        "YTD": "20",
        "LMSD": "3"
    },
    "positive_feedback": {
        "Daily": "5",
        "MTD": "20",
        "WTD": "10",
        "YTD": "80",
        "LMSD": "7"
    },
    "bot_accuracy": {
        "Daily": "88.88",
        "MTD": "84.84",
        "WTD": "90.90",
        "YTD": "88.23",
        "LMSD": "91.66"
    },
}

SESSION_ANALYTICS_DATA = {
    "total_sessions": {
        "Daily": "9",
        "MTD": "33",
        "WTD": "22",
        "YTD": "102",
        "LMSD": "12"
    },
    "avg_session_duration": {
        "Daily": "8 m",
        "MTD": "28 m",
        "WTD": "20 m",
        "YTD": "90 m",
        "LMSD": "11 m"
    },
    "avg_messages_in_session": {
        "Daily": "1",
        "MTD": "5",
        "WTD": "2",
        "YTD": "12",
        "LMSD": "1"
    },
    "total_session_duration": {
        "Daily": "16 m",
        "MTD": "46 m",
        "WTD": "40 m",
        "YTD": "3 h",
        "LMSD": "22 m"
    },
    "total_bot_clicks": {
        "Daily": "24",
        "MTD": "67",
        "WTD": "23",
        "YTD": "120",
        "LMSD": "34"
    },
}

USER_ANALYTICS_DATA = {
    "total_users": {
        "Daily": "9",
        "MTD": "33",
        "WTD": "22",
        "YTD": "102",
        "LMSD": "12"
    },
    "form_filled": {
        "Daily": "8",
        "MTD": "28",
        "WTD": "20",
        "YTD": "90",
        "LMSD": "11"
    },
    "authentication_failure": {
        "Daily": "1",
        "MTD": "5",
        "WTD": "2",
        "YTD": "12",
        "LMSD": "1"
    },
    "authentication_successful": {
        "Daily": "16",
        "MTD": "46",
        "WTD": "40",
        "YTD": "3",
        "LMSD": "22"
    },
    "customer_initiated_conversation": {
        "Daily": "6",
        "MTD": "6",
        "WTD": "4",
        "YTD": "3",
        "LMSD": "22"
    },
    "business_initiated_conversation": {
        "Daily": "5",
        "MTD": "4",
        "WTD": "5",
        "YTD": "6",
        "LMSD": "21"
    }
}

LIVECHAT_ANALYTICS_DATA = {
    "intent_called": {
        "Daily": "9",
        "MTD": "33",
        "WTD": "22",
        "YTD": "102",
        "LMSD": "12"
    },
    "conversion_percent": {
        "Daily": "8%",
        "MTD": "28%",
        "WTD": "20%",
        "YTD": "90%",
        "LMSD": "11%"
    },
    "agent_connected": {
        "Daily": "1",
        "MTD": "5",
        "WTD": "2",
        "YTD": "12",
        "LMSD": "1"
    },
    "request_raised": {
        "Daily": "16",
        "MTD": "46",
        "WTD": "40",
        "YTD": "3",
        "LMSD": "22"
    },
}

MESSAGE_ANALYTICS_CHANNEL_DATA = {
    "total_messages": {
        "Android": "9",
        "Alexa": "33",
        "Facebook": "22",
        "GoogleHome": "102",
        "WhatsApp": "12",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "identified_messages": {
        "Android": "8",
        "Alexa": "28",
        "Facebook": "20",
        "GoogleHome": "90",
        "WhatsApp": "11",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "unidentified_messages": {
        "Android": "1",
        "Alexa": "5",
        "Facebook": "2",
        "GoogleHome": "12",
        "WhatsApp": "1",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "intuitive_messages": {
        "Android": "12",
        "Alexa": "15",
        "Facebook": "12",
        "GoogleHome": "12",
        "WhatsApp": "11",
        "GoogleBusinessMessages": "13",
        "Telegram": "14",
        "Microsoft": "11",
        "Web": "30",
    },
    "negative_feedback": {
        "Android": "2",
        "Alexa": "3",
        "Facebook": "2",
        "GoogleHome": "20",
        "WhatsApp": "3",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "positive_feedback": {
        "Android": "5",
        "Alexa": "20",
        "Facebook": "10",
        "GoogleHome": "80",
        "WhatsApp": "7",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "bot_accuracy": {
        "Android": "88",
        "Alexa": "84",
        "Facebook": "90",
        "GoogleHome": "88",
        "WhatsApp": "91",
        "GoogleBusinessMessages": "100",
        "Telegram": "100",
        "Microsoft": "100",
        "Web": "100",
    },
}

USER_ANALYTICS_CHANNEL_DATA = {
    "total_users": {
        "Android": "9",
        "Alexa": "33",
        "Facebook": "22",
        "GoogleHome": "102",
        "WhatsApp": "12",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "form_filled": {
        "Android": "8",
        "Alexa": "28",
        "Facebook": "20",
        "GoogleHome": "90",
        "WhatsApp": "11",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "authentication_failure": {
        "Android": "1",
        "Alexa": "5",
        "Facebook": "2",
        "GoogleHome": "12",
        "WhatsApp": "1",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "authentication_successful": {
        "Android": "2",
        "Alexa": "3",
        "Facebook": "2",
        "GoogleHome": "20",
        "WhatsApp": "3",
        "GoogleBusinessMessages": 13,
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
    },
    "customer_initiated_conversation": {
        "Android": "0",
        "Alexa": "0",
        "Facebook": "0",
        "GoogleHome": "0",
        "WhatsApp": "3",
        "GoogleBusinessMessages": 0,
        "Telegram": "0",
        "Microsoft": "0",
        "Web": "0",
    },
    "business_initiated_conversation": {
        "Android": "0",
        "Alexa": "0",
        "Facebook": "0",
        "GoogleHome": "0",
        "WhatsApp": "7",
        "GoogleBusinessMessages": 0,
        "Telegram": "0",
        "Microsoft": "0",
        "Web": "0",
    },
}

LIVECHAT_ANALYTICS_CHANNEL_DATA = {
    "intent_called": {
        "Android": "9",
        "Alexa": "33",
        "Facebook": "22",
        "GoogleHome": "102",
        "WhatsApp": "12",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
        "iOS": "9",
        "ET-Source": "22",
        "Twitter": "15",
        "Instagram": "45",
    },
    "conversion_percent": {
        "Android": "8%",
        "Alexa": "28%",
        "Facebook": "20%",
        "GoogleHome": "90%",
        "WhatsApp": "11%",
        "GoogleBusinessMessages": "13%",
        "Telegram": "10%",
        "Microsoft": "1%",
        "Web": "10%",
        "iOS": "20%",
        "ET-Source": "18%",
        "Twitter": "16%",
        "Instagram": "25%",
    },
    "agent_connected": {
        "Android": "1",
        "Alexa": "5",
        "Facebook": "2",
        "GoogleHome": "12",
        "WhatsApp": "1",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
        "iOS": "9",
        "ET-Source": "2",
        "Twitter": "8",
        "Instagram": "7",
    },
    "request_raised": {
        "Android": "2",
        "Alexa": "3",
        "Facebook": "2",
        "GoogleHome": "20",
        "WhatsApp": "3",
        "GoogleBusinessMessages": "13",
        "Telegram": "10",
        "Microsoft": "1",
        "Web": "10",
        "iOS": "9",
        "ET-Source": "22",
        "Twitter": "15",
        "Instagram": "45",
    },
}

FLOW_ANALYTICS_DATA = [
    ["Check Account Balance", "5", "2", "0.4"],
    ["Open Account", "10", "1", "0.1"],
    ["Check Loan amount", "3", "0", "0"],
    ["Apply for Loan", "7", "4", "0.4"],
]

LANGUAGE_ANALYTICS_DATA = {
    "English": [10, 20, 18, 90, 51, 70, 10, 40, 20, 20, 20, 30, 10, 10, 20, 20, 20, 10, 20, 20],
    "Hindi": [10, 5, 4, 80, 51, 70, 80, 30, 30, 10, 40, 10, 80, 10, 20, 20, 20, 10, 20, 20],
    "Marathi": [10, 100, 50, 50, 51, 70, 10, 40, 20, 20, 20, 30, 10, 10, 20, 20, 20, 10, 20, 20]
}

LANGUAGE_ANALYTICS_ROW_HEAD = ["English", "Hindi", "Marathi"]

LANGUAGE_ANALYTICS_INDEX_NAMES = ["Users", "Queries Asked", "Queries Answered", "Bot Accuracy %", "Web", "WhatsApp", "IOS", "Migrosoft Teams", "Google RCS", "Twitter", "Telegram", "Viber", "Google Home", "Android", "Facebook", "ET-Source", "Instagram", "Alexa", "Google Bussiness Messenger"]

LANGUAGE_QUERY_ANALYTICS_DATA = {
    "total_users": "Users",
    "total_queries_asked": "Queries Asked",
    "total_queries_answered": "Queries Answered",
    "bot_accuracy": "Bot Accuracy %",
}

INTENT_ANALYTICS_DATA = [
    ["Check Account Balance", "176", "17%"],
    ["Open Account", "57", "10%"],
    ["Check Loan amount", "43", "7%"],
    ["Apply for Loan", "24", "4%"],
]

TRAFFIC_ANALYTICS_DATA = [
    ["https://www.google.com", "https://www.google.com/", "0", "0", "0"],
    ["https://www.google.com", "https://www.google.com", "0", "0", "0"],
    ["https://www.google.com", "https://www.google.com", "0", "0", "0"],
    ["https://www.google.com", "https://www.google.com", "0", "0", "0"],
]

DOWNLOAD_REPORTS_DATA = {
    "bot_queries": "/files/sample_data/BotUnansweredQueries_Sample.xls",
    "unanswered": "/files/sample_data/BotUserMessageHistory_Sample.xls",
    "dropoff": "/files/sample_data/UserSpecificDropOff_Sample.csv",
    "language_analytics": "/files/sample_data/LanguageAnalyticsData_Sample.zip",
    "csat_data": "/files/sample_data/CSATData_sample.csv",
}

WORD_CLOUD_DATA = '<div><a href="https://www.wsj.com/articles/afghanistans-womens-soccer-team-kabul-airport-taliban-11630690627?mod=hp_lead_pos7"><img src="https://images.wsj.net/im-395637?width=620&amp;height=413" alt="Afghanistan’s Women’s Soccer Team Knew It Had to Get Out. ‘Burn Your Jerseys.’" /></a></div><div><h3><a href="https://www.wsj.com/articles/afghanistans-womens-soccer-team-kabul-airport-taliban-11630690627?mod=hp_lead_pos7"><span>Afghanistan’s Women’s Soccer Team Knew It Had to Get Out. ‘Burn Your Jerseys.’</span></a></h3></div><div><p><span>A daring evacuation plan for the teammates—once symbols of a new Afghanistan—faced danger at every step. Coordinating it all was a former player thousands of miles away, with no wealthy benefactors and few contacts.</span><span><a href="https://www.wsj.com/articles/afghanistans-womens-soccer-team-kabul-airport-taliban-11630690627?mod=hp_lead_pos7#comments_sector"><span>143</span></a><span><span>Long read</span></span></span></p></div><ul><li><h4><a href="https://www.wsj.com/articles/taliban-press-last-afghan-resistance-fighters-in-north-11630676104?mod=hp_lead_pos8">Taliban Press Last Afghan Resistance Fighters in North</a></h4></li></ul>'

EMAIL_EXCEL_PATH = 'EasyChatApp/email-excels/'

EMAIL_REPORT_BUTTON = '<a class="easychat-mailer-download-reports-btn" href="()">Download {}</a>'

LOCALHOST = "http://127.0.0.1:8000"
