CHAT_SENDER = (("agent", "agent"), ("client",
               "client"), ("system", "System"))

COGNOMEET_ACCESS_TOKEN = 'CognoMeet access token'

COGNO_MEET_ORGANIZATION_ID = '856d1b01-ec2d-4e4f-8d87-4f60c52e4f93'

COGNO_MEET_API_KEY = '2b8210b0c384f1f65944'

COGNO_MEET_BASE_URL = 'https://api.cluster.dyte.in/v1'

COGNO_MEET_BASE_URL_V2 = 'https://api.cluster.dyte.in/v2'

MAXIMUM_PARTICIPANTS_LIMIT = 5

"""
This specifies the max number of rows that can be written
on an excel sheet at a given point of time. If the rows count
exceeds beyond the below limit then we register the request of
the export and provide the report over mail.
"""
REPORT_GENERATION_CAP = 500

# Timers
COMMON_INACTIVITY_TIMER = 10

# Cronjobs IDs

COGNOMEET_ARCHIVE_MEETINGS = "CRJ_1_COGNOMEET_ARCHIVE_MEETINGS"

COGNOMEET_FETCH_RECORDINGS = "CRJ_2_COGNOMEET_FETCH_RECORDINGS"

COGNOMEET_SUPPORT_HISTORY = "CRJ_3_COGNOMEET_SUPPORT_HISTORY"

COGNOMEET_ANALYTICS = "CRJ_4_COGNOMEET_ANALYTICS"

MEETING_STATUS = (("scheduled", "scheduled"), ("completed", "completed"))

NO_AGENT_PERMIT_MEETING_TOAST_TEXT = 'Please wait the meeting host will let you in soon'

USER = 'EasyChatApp.User'

UNIQUE_ACCESS_TOKEN_KEY = "unique access token key"

USER_CHOICES = (("agent", "agent"), ("supervisor",
                                     "supervisor"), ("admin", "admin"), ("admin_ally", "admin_ally"))

COGNOMEETAPP_MEETING_FILES_PATH = "secured_files/CognoMeetApp/meeting"

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

REPORT_TYPE_CHOICES = (
    ("meeting-support-history", "meeting-support-history"),
    ("meeting-analytics", "meeting-analytics")
)

GOOGLE_GEOCODER_KEY = "AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ"

SECURED_FILES_PATH = "secured_files/"

COGNOMEET_RECORDINGS_PATH = "secured_files/CognoMeetApp/meeting_recordings"

DATE_TIME_FORMAT = "%Y-%m-%d"

CUSTOMER_NAME = "Customer Name"

CUSTOMER_MOBILE_NUMBER = "Customer Mobile Number"

MEETING_SUPPORT_HISTORY_PER_PAGE_COUNT = 20

DEFAULT_COGNOMEET_LOGO = "/static/DeveloperConsoleApp/img/cognomeet-logo.svg"

DEFAULT_COGNOMEET_TAB_LOGO = "/static/DeveloperConsoleApp/img/cognomeet-favicon.svg"

DEFAULT_COGNOMEET_TITLE_TEXT = "Cogno Meet"

COGNOAI_LOGO_WHITE = "/files/CognoMeetApp/img/cognoai_logo_white.png"

DEFAULT_API_TIMEOUT_TIME = 10

FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT = 24  # In Hours
