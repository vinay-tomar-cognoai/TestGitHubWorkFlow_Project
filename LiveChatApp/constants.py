from datetime import datetime

ROLES = (("1", "Live-Chat Admin"),
         ("2", "Live-Chat Supervisor"), ("3", "Live-Chat Agent"))

LIVECHAT_LEVEL = (("1", "L1"), ("2", "L2"), ("3", "L3"))

LIVECHAT_EVENT_TYPE = (("1", "Working"), ("2", "Holiday"), )

CANNED_RESPONSE_STATUS = (("private", "Private"), ("public", "Public"))

STOP_INTERACTION = "Stop Interaction"

REPRESENTATIVE_SYSTEM_MESSAGE = "Our chat representatives are busy right now. Please try again in some time."

USER_ONLINE_OFFLINE = 'Designates whether user is online or not.'

UNIQUE_SESSION_ID = 'unique session_id'

RGB_25_103_210_01 = "rgb(25, 103, 210, 0.1)"

APPLICATION_JSON = 'application/json'

DELETE_PROFILE = "Deleted Profile"

DATE_YYYY_MM_DD = "%Y-%m-%d"

DATE_DD_MMM_YY = "%d-%b-%y"

DATE_DD_MMM_YYYY = "%d-%b-%Y"

DATE_15_08_21_08 = "(15/08/21 - 21/08/21)"

INTERACTION_PER_CHAT = "Interaction Per Chat"

EMAIL_EXCEL_PATH = 'LiveChatApp/email-excels/'

CHAT_LOGIN_PATH = "/chat/login/"

AUTHORIZATION_DENIED = "You are not authorised to access this page."

INTERNAL_SERVER_ERROR = "Internal Server Error!"

INVALID_OPERATION = "Invalid Operation"

FILE_UPLOAD_ERROR = "Please upload file in correct format."

NOT_ALLOWED_IN_CANNED_RESPONSE = " are not allowed in canned response"

EXCEEDING_CHARACTER_LIMIT = "Exceeding character limit of "

CHARACTERS_IN_KEYWORD = " characters in keyword"

KEYWORD_CANNOT_BE_EMPTY = "Keyword list cannot be empty."

CHARACTERS_IN_CANNED_RESPONSE = " characters in canned response"

CANNED_RESPONSE_CANNOT_BE_EMPTY = "Canned Response cannot be empty."

USER_LOGGED_OUT = "7"

ACCESS_DENIED = "Access denied"

STATIC_MISSED_CHATS_REPORT_PATH = "LiveChatApp/static_missed_chats_report.html"

LIVECHAT_CHAT_HISTORY_PATH = "livechat-chat-history/"

LIVECHAT_CONVERSATION_PATH = "livechat-conversations/"

CHAT_HISTORY_PATH = "/chat_history_"

FILES_LIVECHAT_CHAT_HISTORY = "/files/livechat-chat-history/"

FILES_LIVECHAT_CONVERSATION = "/files/livechat-conversations/"

LIVECHAT_CONVERSATION_FILE_NAME = "/LiveChat_Conversations_"

LIVECHAT_MISSED_CHATS_REPORT_PATH = "livechat-missed-chats-report/"

MISSED_CHATS_REPORT_PATH = "/missed_chats_report_"

FILES_MISSED_CHATS_REPORT = "/files/livechat-missed-chats-report/"

LIVECHAT_OFFLINE_CHATS_REPORT = "livechat-offline-chats-report/"

OFFLINE_CHATS_REPORT = "/offline_chats_report_"

FILES_OFFLINE_CHATS_REPORT = "/files/livechat-offline-chats-report/"

LIVECHAT_ABANDONED_CHATS_REPORT_PATH = "livechat-abandoned-chats-report/"

ABANDONED_CHATS_REPORT_PATH = "/abandoned_chats_report_"

FILES_ABANDONED_CHATS_REPORT_PATH = "/files/livechat-abandoned-chats-report/"

LIVECHAT_LOGIN__LOGOUT_REPORT_PATH = "livechat-login-logout-report/"

LOGIN_LOGOUT_REPORT_PATH = "/login_logout_report_"

FILES_LOGIN_LOGOUT_REPORT_PATH = "/files/livechat-login-logout-report/"

LIVECHAT_AGENT_NOT_READY_REPORT_PATH = "livechat-agent-not-ready-report/"

AGENT_NOT_READY_REPORT_PATH = "/agent_not_ready_report_"

FILES_AGENT_NOT_READY_REPORT_PATH = "/files/livechat-agent-not-ready-report/"

LIVECHAT_AGENT_PERFORMANCE_REPORT_PATH = "livechat-agent-performance-report/"

AGENT_PERFORMANCE_REPORT = "/agent_performance_report_"

FILES_AGENT_PERFORMANCE_REPORT = "/files/livechat-agent-performance-report/"

LIVECHAT_HOURLY_INTERACTION_REPORT = "livechat-hourly-interaction-report/"

HOURLY_INTERACTION_REPORT = "/hourly_interaction_report_"

FILES_HOURLY_INTERACTION_REPORT = "/files/livechat-hourly-interaction-report/"

LIVECHAT_ANALYTICS_DATA_PATH = "livechat-analytics-data/"

ANALYTICS_PATH = "/analytics_"

FILES_ANALYTICS_PATH = "/secured_files/LiveChatApp/livechat-analytics-data/"

CHAT_ANALYTICS_PATH = "/secured_files/LiveChatApp/livechat-chat-history/"

LIVECHAT_DAILY_INTERACTION_REPORT_PATH = "livechat-daily-interaction-report/"

DAILY_INTERACTION_REPORT_PATH = "/daily_interaction_report_"

FILES_DAILY_INTERACTION_REPORT_PATH = "/files/livechat-daily-interaction-report/"

LIVECHAT_VOIP_HISTORY_PATH = "livechat-voip-history/"

VOIP_HISTORY_PATH = "/voip_history_"

FILES_VOIP_HISTORY_PATH = "/files/livechat-voip-history/"

AGENT_CURRENT_STATUS = (("0", STOP_INTERACTION), ("1", "Lunch"), ("2", "Coffee"), ("3", "Adhoc"),
                        ("4", "Meeting"), ("5", "Training"), ("6", "Working"))

LIVECHAT_SENDER = (("Agent", "Agent"), ("Customer", "Customer"),
                   ("System", "System"), ("Bot", "Bot"), ("Supervisor", "Supervisor"))

VIDEO_CALL_MESSAGE_FOR = (
    ("primary_agent", "Primary Agent"),
    ("guest_agent", "Guest Agent"),
    ("customer", "Customer")
)

LIVECHAT_REPORT_TYPE = (("0", "AGENT NOT READY REPORT"), ("1", "AGENT PERFORMANCE REPORT"),
                        ("2", "LIVECHAT HISTORY"), ("3",
                                                    "DAILY INTERACTION REPORT"),
                        ("4", "HOURLY INTERACTION REPORT"), ("5",
                                                             "LOGIN LOGOUT REPORT"), ("6", "OFFLINE MESSAGE REPORT"),
                        ("7", "LIVECHAT ANALYTICS DATA"), ("8", "ABANDONED CHATS REPORT"), ("9", "TOTA DECLINED CHATS REPORT"), ("10", "VOIP HISTORY"),
                        ("11", "VC HISTORY"), ("12", "COBROWSING HISTORY"))

LIVECHAT_GUEST_AGENT = (("1", "1"), ("2", "2"), ("3", "3"))

LIVECHAT_SOURCE_OF_INCOMING_REQUEST = (
    ("1", "Desktop"),
    ("2", "Mobile"),
    ("3", "Others")
)

CATEGORY_ITEM_COUNT = 10

CANNED_RESPONSE_ITEM_COUNT = 10

AUDIT_TRAIL_ITEM_COUNT = 10

VOIP_HISTORY_ITEM_COUNT = 10

ARCHIVE_CUSTOMER_ITEM_COUNT = 10

LIVECHAT_ONLY_ADMIN_ITEM_COUNT = 10

AGENT_ITEM_COUNT = 200

CALENDER_ITEM_COUNT = 31

OFFLINE_MESSAGE_COUNT = 10

TOTAL_CUSTOMER_DECLINED_CHATS_COUNT = 10

ABANDONED_CHATS_COUNT = 10

BLACKLISTED_KEYWORD_COUNT = 10

SESSION_MANAGEMENT_ITEM_COUNT = 10

AGENT_NOT_READY_REPORT_ITEM_COUNT = 10

AGENT_PERFORMANCE_REPORT_ITEM_COUNT = 10

DAILY_INTERACTION_REPORT_ITEM_COUNT = 10

VIDEO_CALL_COUNT = 10

DEFAULT_AGENT_CONNECTION_RATE = 80

QUEUE_REQUESTS_COUNT = 10

FOLLOWUP_LEADS_COUNT = 10

REPORTED_USERS_COUNT = 10

BLOCKED_USERS_COUNT = 10

LIVECHAT_AUDIT_TRAIL_ACTIONS = (
    ("0", STOP_INTERACTION),
    ("1", "Lunch"),
    ("2", "Coffee"),
    ("3", "Adhoc"),
    ("4", "Meeting"),
    ("5", "Training"),
    ("6", "Working"),
    ("7", "Logged In"),
    ("8", "Logged Out"),
    ("9", "Marked Offiline by Supervisor"),
    ("10", "Marked Offiline by Admin")
)

PRIORITY_VALUES = (
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5")
)

LIVECHAT_AUDIT_TRAIL_ACTION_DICT = {
    "0": STOP_INTERACTION,
    "1": "Lunch",
    "2": "Coffee",
    "3": "Adhoc",
    "4": "Meeting",
    "5": "Training",
    "6": "Working",
    "7": "Logged In",
    "8": "Logged Out",
    "9": "Marked Offiline by Supervisor",
    "10": "Marked Offiline by Admin",
}

DEFAULT_DATE_FORMAT = "%Y-%m-%d"

LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT = 500
LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT = 25
LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT = 100
LIVECHAT_MAX_CUSTOMER_ALLOWED_FOR_AGENT = 100

ADD_USER = "add_user"
REMOVE_USER = "remove_user"
CREATE_GROUP = "create_group"
DELETE_GROUP = "delete_group"
EDIT_GROUP = "edit_group"
REMOVE_GROUP = "remove_group"
EXIT_GROUP = "exit_group"


GROUP_ACTIVITIES = (
    (ADD_USER, "Add User to Group"),
    (REMOVE_USER, "Remove User from Group"),
    (CREATE_GROUP, "Create Group"),
    (DELETE_GROUP, "Delete Group"),
    (EDIT_GROUP, "Edit Group"),
    (REMOVE_GROUP, "Remove Group"),
    (EXIT_GROUP, "Exit Group"),
)

CALL_TYPE = (("none", "None"), ("pip", "PIP Voice Call"), ("new_tab", "New Tab Voice Call"), ("video_call", "Video Call"))

VOIP_INITIATOR = (("customer", "Customer"), ("agent", "Agent"))

BLACKLIST_KEYWORD_FOR = (("customer", "Customer"), ("agent", "Agent"))

CUSTOMER_BLOCK_DURATION = (("1", "30 mins"), ("2", "60 mins"), ("3", "1 Day"), ("4", "7 Days"), ("5", "14 Days"))

EMAIL_SETUP_SECURITY = (("ssl", "SSL"), ("tls", "TLS"))

FILE_ACCESS_TYPES = (
    ("all", "All"), 
    ("group_chat", "Group Chat"), 
    ("user_group_chat", "User Group Chat"),
    ("personal_access", "Personal Access")
)

CUSTOMER_LEFT_THE_CHAT = "Customer left the chat"

LIVECHAT_SECURED_FILES_ATTACHMENT_PATH = "secured_files/LiveChatApp/attachment/"

DATE_DD_MM_YYYY = "%d-%m-%Y"

LIVECHAT_AGENT_PERFORMANCE_REPORT_FOLDER = "livechat-agent-performance-report/"

DATE_DD_MM_YYYY_TIME_HH_MIN_P = "%d/%m/%Y, %I:%M:%p"

DATE_DD_MMM_YYYY_TIME_HH_MIN_P = "%d-%b-%Y, %I:%M %p" 

AGENT_LEFT_THE_CHAT_TEXT = "Agent has left the session. LiveChat session ended."

TRANSCRIPT_MAIL_TEXT = "The transcript will be sent over mail"

NO_SESSION_EXIST_TEXT = "No such session exists."

CUSTOMER_LEFT_THE_CHAT_TEXT = "customer left the chat"

AGENT_ASSIGNED_EVENT = 'ASSIGN_AGENT'

SEND_MESSAGE_EVENT = 'SEND_MESSAGE'

END_CHAT_EVENT = 'END_CHAT'

TRANSFER_CHAT_EVENT = 'TRANSFER_CHAT'

ADD_AGENT_EVENT = 'ADD_GUEST_AGENT'

EXIT_AGENT_EVENT = 'EXIT_GUEST_AGENT'

INACTIVITY_EVENT = 'INACTIVITY_END_CHAT'

CHAT_RESOLVED_BY_AGENT = "agent resolved the chat"

WARNING_MESSAGE_NOTIF = "warning text sent to the user"

REPORT_MESSAGE_NOTIF = "chat has been reported"

WHATSAPP_REINITIATING_MESSAGE = "reinitiating request sent"

LIVECHAT_DOCUMENTS = {
    "create-customer": {
        "url_suffix": "create-customer",
        "original_file_name": "Create_Customer_API.docx",
        "display_file_name": "Create Customer API.docx",
    },
    "save-chat": {
        "url_suffix": "save-chat",
        "original_file_name": "Save_Chat_API.docx",
        "display_file_name": "Save Chat API.docx",
    },
    "end-chat": {
        "url_suffix": "end-chat",
        "original_file_name": "End_Chat_API.docx",
        "display_file_name": "End Chat API.docx",
    },
    "save-feedback": {
        "url_suffix": "save-feedback",
        "original_file_name": "Save_Feedback_API.docx",
        "display_file_name": "Save Feedback API.docx",
    },
    "update-event": {
        "url_suffix": "update-livechat-event",
        "original_file_name": "Update_Events_API.docx",
        "display_file_name": "Update Events API.docx",
    },
    "analytics-collection": {
        "url_suffix": "analytics-collection",
        "original_file_name": "LiveChat_Analytics_Postman_Collection.json",
        "display_file_name": "LiveChat Analytics Postman Collection.json",
    }
}

LIVECHAT_DOCUMENTS_PATH = "secured_files/LiveChatApp/livechat-documents/"

LIVECHAT_VC_HISTORY_PATH = "livechat-vc-history/"

VC_HISTORY_PATH = "/vc_history_"

FILES_VC_HISTORY_PATH = "/files/livechat-vc-history/"

LIVECHAT_VC_FILES_PATH = 'secured_files/LiveChatApp/video_calls'

COBROWSING_REQUEST_TEXT = "We would like to assist you in filling your form. By clicking Accept our Customer Service Agent will be able to see your screen and assist you.Please don’t worry, your personal data is safe and will not be visible to our Agent"

LIVECHAT_COBROWSING_HISTORY_PATH = "livechat-cobrowsing-history/"

COBROWSING_HISTORY_PATH = "/cobrowsing_history_"

FILES_COBROWSING_HISTORY_PATH = "/files/livechat-cobrowsing-history/"

DEFAULT_CUSTOMER_BLACKLISTED_KEYWORDS = ['4r5e', '5h1t', '5hit', 'a55', 'anal', 'anus', 'ar5e', 'arrse', 'arse', 'ass', 'ass-fucker', 'asses', 'assfucker', 'assfukka', 'asshole', 'assholes', 'asswhole', 'a_s_s', 'b!tch', 'b00bs', 'b17ch', 'b1tch', 'ballbag', 'balls', 'ballsack', 'bastard', 'beastial', 'beastiality', 'bellend', 'bestial', 'bestiality', 'bi+ch', 'biatch', 'bitch', 'bitcher', 'bitchers', 'bitches', 'bitchin', 'bitching', 'bloody', 'blow job', 'blowjob', 'blowjobs', 'boiolas', 'bollock', 'bollok', 'boner', 'boob', 'boobs', 'booobs', 'boooobs', 'booooobs', 'booooooobs', 'breasts', 'buceta', 'bugger', 'bum', 'bunny fucker', 'butt', 'butthole', 'buttmunch', 'buttplug', 'c0ck', 'c0cksucker', 'carpet muncher', 'cawk', 'chink', 'cipa', 'cl1t', 'clit', 'clitoris', 'clits', 'cnut', 'cock', 'cock-sucker', 'cockface', 'cockhead', 'cockmunch', 'cockmuncher', 'cocks', 'cocksuck', 'cocksucked', 'cocksucker', 'cocksucking', 'cocksucks', 'cocksuka', 'cocksukka', 'cok', 'cokmuncher', 'coksucka', 'coon', 'cox', 'crap', 'cum', 'cummer', 'cumming', 'cums', 'cumshot', 'cunilingus', 'cunillingus', 'cunnilingus', 'cunt', 'cuntlick', 'cuntlicker', 'cuntlicking', 'cunts', 'cyalis', 'cyberfuc', 'cyberfuck', 'cyberfucked', 'cyberfucker', 'cyberfuckers', 'cyberfucking', 'd1ck', 'damn', 'dick', 'dickhead', 'dildo', 'dildos', 'dink', 'dinks', 'dirsa', 'dlck', 'dog-fucker', 'doggin', 'dogging', 'donkeyribber', 'doosh', 'duche', 'dyke', 'ejaculate', 'ejaculated', 'ejaculates', 'ejaculating', 'ejaculatings', 'ejaculation', 'ejakulate', 'f u c k', 'f u c k e r', 'f4nny', 'fag', 'fagging', 'faggitt', 'faggot', 'faggs', 'fagot', 'fagots', 'fags', 'fanny', 'fannyflaps', 'fannyfucker', 'fanyy', 'fatass', 'fcuk', 'fcuker', 'fcuking', 'feck', 'fecker', 'felching', 'fellate', 'fellatio', 'fingerfuck', 'fingerfucked', 'fingerfucker', 'fingerfuckers', 'fingerfucking', 'fingerfucks', 'fistfuck', 'fistfucked', 'fistfucker', 'fistfuckers', 'fistfucking', 'fistfuckings', 'fistfucks', 'flange', 'fook', 'fooker', 'fuck', 'fucka', 'fucked', 'fucker', 'fuckers', 'fuckhead', 'fuckheads', 'fuckin', 'fucking', 'fuckings', 'fuckingshitmotherfucker', 'fuckme', 'fucks', 'fuckwhit', 'fuckwit', 'fudge packer', 'fudgepacker', 'fuk', 'fuker', 'fukker', 'fukkin', 'fuks', 'fukwhit', 'fukwit', 'fux', 'fux0r', 'f_u_c_k', 'gangbang', 'gangbanged', 'gangbangs', 'gaylord', 'gaysex', 'goatse', 'god-dam', 'god-damned', 'goddamn', 'goddamned', 'hardcoresex', 'hell', 'heshe', 'hoar', 'hoare', 'hoer', 'homo', 'hore', 'horniest', 'horny', 'hotsex', 'jack-off', 'jackoff', 'jap', 'jerk-off', 'jism', 'jiz', 'jizm', 'jizz', 'kawk', 'knob', 'knobead', 'knobed', 'knobend', 'knobhead', 'knobjocky', 'knobjokey', 'kock', 'kondum', 'kondums', 'kum', 'kummer', 'kumming', 'kums', 'kunilingus', 'kiunt', 'l3i+ch', 'l3itch', 'labia', 'lmfao', 'lust', 'lusting', 'm0f0', 'm0fo', 'm45terbate', 'ma5terb8', 'ma5terbate', 'masochist', 'master-bate', 'masterb8', 'masterbat*', 'masterbat3', 'masterbate', 'masterbation', 'masterbations', 'masturbate', 'mo-fo', 'mof0', 'mofo', 'mothafuck', 'mothafucka', 'mothafuckas', 'mothafuckaz', 'mothafucked', 'mothafucker', 'mothafuckers', 'mothafuckin', 'mothafucking', 'mothafuckings', 'mothafucks', 'mother fucker', 'motherfuck', 'motherfucked', 'motherfucker', 'motherfuckers', 'motherfuckin', 'motherfucking', 'motherfuckings', 'motherfuckka', 'motherfucks', 'muff', 'mutha', 'muthafecker', 'muthafuckker', 'muther', 'mutherfucker', 'n1gga', 'n1gger', 'nazi', 'nigg3r', 'nigg4h', 'nigga', 'niggah', 'niggas', 'niggaz', 'nigger', 'niggers', 'nob', 'nob jokey', 'nobhead', 'nobjocky', 'nobjokey', 'numbnuts', 'nutsack', 'orgasim', 'orgasims', 'orgasm', 'orgasms', 'p0rn', 'pawn', 'pecker', 'penis', 'penisfucker', 'phonesex', 'phuck', 'phuk', 'phuked', 'phuking', 'phukked', 'phukking', 'phuks', 'phuq', 'pigfucker', 'pimpis', 'piss', 'pissed', 'pisser', 'pissers', 'pisses', 'pissflaps', 'pissin', 'pissing', 'pissoff', 'poop', 'porn', 'porno', 'pornography', 'pornos', 'prick', 'pricks', 'pron', 'pube', 'pusse', 'pussi', 'pussies', 'pussy', 'pussys', 'rectum', 'retard', 'rimjaw', 'rimming', 's hit', 's.o.b.', 'sadist', 'schlong', 'screwing', 'scroat', 'scrote', 'scrotum', 'semen', 'sex', 'sh!+', 'sh!t', 'sh1t', 'shag', 'shagger', 'shaggin', 'shagging', 'shemale', 'shi+', 'shit', 'shitdick', 'shite', 'shited', 'shitey', 'shitfuck', 'shitfull', 'shithead', 'shiting', 'shitings', 'shits', 'shitted', 'shitter', 'shitters', 'shitting', 'shittings', 'shitty', 'skank', 'slut', 'sluts', 'smegma', 'smut', 'snatch', 'son-of-a-bitch', 'spac', 'spunk', 's_h_i_t', 't1tt1e5', 't1tties', 'teets', 'teez', 'testical', 'testicle', 'tit', 'titfuck', 'tits', 'titt', 'tittie5', 'tittiefucker', 'titties', 'tittyfuck', 'tittywank', 'titwank', 'tosser', 'turd', 'tw4t', 'twat', 'twathead', 'twatty', 'twunt', 'twunter', 'v14gra', 'v1gra', 'vagina', 'viagra', 'vulva', 'w00se', 'wang', 'wank', 'wanker', 'wanky', 'whoar', 'whore', 'willies', 'willy', 'xrated', 'xxx']

LIVECHAT_EMAIL_CHAT_DEFAULT_SUBJECT = "Greetings from LiveChat"

DAYS_IN_WEEK = 7

RATE_LIMIT_FOR_EXTERNAL_API_IN_ONE_MINUTE = 100

AUTH_TOKEN_ACCESS_TYPE_CHOICES = (
    ("1", "Auth Token Generation"),
    ("2", "Analytics Access")
)

EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT = 20  # In Seconds

EXTERNAL_API_TOKEN_CREATION_LIMIT_PER_MINUTE = 100

AUTH_TOKEN_VALIDITY_DURATION = 6  # In Hours

LIVECHAT_COMBINED_CRONJOB_CONSTANT = 'livechat_combined_cronjob'

LIVECHAT_SEND_MAIL_CRONJOB_CONSTANT = 'livechat_send_mail_analytics'

LIVECHAT_ASSIGN_CHAT_SCHEDULER = 'livechat_assign_chat_scheduler'

LIVECHAT_ASSIGN_FOLLOWUP_LEAD_SCHEDULER = 'livechat_assign_followup_lead_scheduler'

LIVECHAT_RETRIEVE_EMAIL_SCHEDULER = 'livechat_retrieve_email_scheduler'

CRONJOB_TRACKER_EXPIRY_TIME_LIMIT = 5  # In mins

AMEYO_CHANNELS = {"Web": "webChat", "WhatsApp": "whatsapp"}

LIVECHAT_USER_CREATION_MAX_LIMIT_ALERT_TEXT = "Your limit is max out for adding user to this account"  # Limit configured in LiveChatAdminConfig object

FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT_LIVECHAT = 24  # In Hours

SECURED_FILES_PATH = '/secured_files/'

RESPONSE_SENTENCE_SEPARATOR = '$$$'

DAYS_LIMIT_FOR_KAFKA = 60

LIVECHAT_FACEBOOK_CHAR_LIMIT = 2000

LIVECHAT_INSTAGRAM_CHAR_LIMIT = 1000

FILES_PATH = 'files/'

STOP_CONVERSATION_LIST = {'af': 'klets beëindig', 'sq': 'mbylli bisedën', 'am': 'ውይይትን ጨርስ', 'ar': 'نهاية المحادثة', 'hy': 'վերջ զրույցը', 'az': 'söhbəti bitir', 'eu': 'txata amaitu', 'be': 'скончыць чат', 'bn': 'চ্যাট শেষ করুন', 'bs': 'završi chat', 'bg': 'край на чата', 'ca': 'acabar el xat', 'ceb': 'tapuson ang chat', 'zh': '结束聊天', 'zh-TW': '結束聊天', 'co': 'finisce u chat', 'hr': 'završiti razgovor', 'cs': 'ukončit chat', 'da': 'afslutte chat', 'nl': 'einde gesprek', 'en': 'end chat', 'eo': 'fini babiladon', 'et': 'lõpeta vestlus', 'fi': 'lopeta chat', 'fr': 'mettre fin à la discussion', 'fy': 'ein petear', 'gl': 'finalizar o chat', 'ka': 'ჩატის დასრულება', 'de': 'Ende des Gesprächs', 'el': 'τέλος συνομιλίας', 'gu': 'ચેટ સમાપ્ત કરો', 'ht': 'fini chat', 'ha': 'karshen hira', 'haw': 'hoʻopau kamaʻilio', 'he': 'סיים שיחה', 'hi': 'बातचीत बंद करें', 'hmn': 'xaus kev sib tham', 'hu': 'befejezni a csevegést', 'is': 'enda spjallið', 'ig': 'kwusi nkata', 'id': 'Akhiri Obrolan', 'ga': 'deireadh comhrá', 'it': 'chiudi la chat', 'ja': 'チャットを終了する', 'jv': 'mungkasi chatting', 'kn': 'ಅಂತ್ಯ ಚಾಟ್', 'kk': 'чатты аяқтау', 'km': 'បញ្ចប់ការជជែក', 'rw': 'ikiganiro cya nyuma', 'ko': '채팅 종료', 'ku': 'dawî chat', 'ky': 'аягы Чат', 'lo': 'ສິ້ນສຸດການສົນທະນາ', 'lv': 'beigt tērzēšanu', 'lt': 'baigti pokalbį', 'lb': 'Enn Chat', 'mk': 'заврши разговор', 'mg': 'farano ny chat', 'ms': 'tamatkan sembang', 'ml': 'ചാറ്റ് അവസാനിപ്പിക്കുക', 'mt': 'tmiem iċ-chat', 'mi': 'mutu te korerorero', 'mr': 'गप्पा संपवा', 'mn': 'чатыг дуусгах', 'my': 'စကားစမြည်အဆုံးသတ်', 'ne': 'च्याट अन्त्य गर्नुहोस्', 'no': 'avslutte chat', 'ny': 'maliza macheza', 'or': 'ଶେଷ ଚାଟ୍ |', 'ps': 'چټ پای', 'fa': 'پایان چت', 'pl': 'zakończ czat', 'pt': 'fim de papo', 'pa': 'ਗੱਲਬਾਤ ਖਤਮ ਕਰੋ', 'ro': 'incheierea convorbirii', 'ru': 'конец чат', 'sm': 'faaiu talanoaga', 'gd': 'deireadh còmhradh', 'sr': 'заврши ћаскање', 'st': 'Qetella moqoqo', 'sn': 'end chat', 'sd': 'گپ ختم ڪريو', 'si': 'කතාබස් අවසන් කරන්න', 'sk': 'ukončiť chat', 'sl': 'končaj klepet', 'so': 'dhame sheekeysiga', 'es': 'Chat finalizado', 'su': 'tungtung obrolan', 'sw': 'kumaliza mazungumzo', 'sv': 'avsluta chat', 'tl': 'tapusin ang chat', 'tg': 'хотимаи сӯҳбат', 'ta': 'அரட்டையை முடிக்கவும்', 'tt': 'ахыргы чат', 'te': 'చాట్ ముగించు', 'th': 'จบการสนทนา', 'tr': 'sohbeti bitir', 'tk': 'ahyrky söhbetdeşlik', 'uk': 'завершити чат', 'ur': 'چیٹ ختم', 'ug': 'ئاخىرقى پاراڭ', 'uz': 'suhbatni tugatish', 'vi': 'kết thúc trò chuyện', 'cy': 'diwedd sgwrs', 'xh': 'phelisa incoko', 'yi': 'סוף שמועסן', 'yo': 'ipari iwiregbe', 'zu': 'qeda ingxoxo'}

END_CHAT_PRESERVER = "<span translate='no'>end_chat</span>"

END_CHAT_MATCHER = "end_chat"
