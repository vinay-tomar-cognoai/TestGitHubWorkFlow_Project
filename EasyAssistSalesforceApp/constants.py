import datetime

CLIENT_DISCONNECTED_TIME_OUT = 600  # 10 min client disconnected timeout

AGENT_DISCONNECTED_TIME_OUT = 600  # 10 min agent disconnected timeout

ARCHIVE_COBROWSE_IO_TIME = 3600  # 1 hour archive cobrowse io request

USER_CHOICES = (("agent", "agent"), ("supervisor",
                                     "supervisor"), ("admin", "admin"))

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

FLOATING_BUTTON_POSITION = (("left", "left"), ("right", "right"))

COBROWSING_LOGIN_ACTION = "1"
COBROWSING_LOGOUT_ACTION = "2"
COBROWSING_ADDUSER_ACTION = "3"
COBROWSING_DELETEUSER_ACTION = "4"
COBROWSING_CHANGESETTINGS_ACTION = "5"
COBROWSING_CHANGEAPPCONFIG_ACTION = "6"
COBROWSING_UPDATEUSER_ACTION = "7"

COBROWSING_ACTION_LIST = ((COBROWSING_LOGIN_ACTION, "Login"),
                          (COBROWSING_LOGOUT_ACTION, "Logout"),
                          (COBROWSING_ADDUSER_ACTION, "Add-User"),
                          (COBROWSING_DELETEUSER_ACTION, "Delete-User"),
                          (COBROWSING_CHANGESETTINGS_ACTION, "Change-Settings"),
                          (COBROWSING_CHANGEAPPCONFIG_ACTION, "Change-App-Config"),
                          (COBROWSING_UPDATEUSER_ACTION, "Updated-User"))


COBROWSING_ACTION_DICT = {}

for action_key, action_value in COBROWSING_ACTION_LIST:
    COBROWSING_ACTION_DICT[action_key] = action_value

COBROWSING_REVERSE_ACTION_DICT = {}

for action_key, action_value in COBROWSING_ACTION_LIST:
    COBROWSING_REVERSE_ACTION_DICT[action_value] = action_key


COBROWSING_AGENT_SUPPORT = (("L1", "L1"), ("L2", "L2"), ("L3", "L3"))

COBROWSING_AGENT_SUPPORT_DICT = {}

for support_key, support_value in COBROWSING_AGENT_SUPPORT:
    COBROWSING_AGENT_SUPPORT_DICT[support_key] = support_value

COBROWSING_HTML_FIELD_TAG = (
    ("input", "input"), ("textarea", "textarea"), ("select", "select"))

COBROWSING_HTML_FIELD_TYPE = (
    ("primary", "primary"), ("secondary", "secondary"))

DEFAULT_APP_COBROWSING_CUSTOMER_SHARE_MESSAGE = "Dear Customer,\n\nPlease click on the link below to virtually connect with our sales representative:\n\n{/customer_link/}\n\nBy clicking on the link above, you are giving consent to connect with our sales representative"

DEFAULT_APP_COBROWSING_EXPERT_SHARE_MESSAGE = "Dear Expert,\n\nPlease click on the link below to virtually connect with our sales representative:\n\n{/expert_link/}"
