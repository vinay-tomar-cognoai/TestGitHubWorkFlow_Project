import os

import json

from elasticsearch import Elasticsearch

from corsheaders.defaults import default_headers

from DeveloperConsoleApp.utils_project_dirs import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^r(53k&)2&lkyb3las722c*@yf7%2b^n-39v%njothx9%p&h=d'

DEBUG = True

EASYCHAT_VERSION = "6.4"

# APPEND DATE AFTER FREEZE

EASYCHAT_DATE_OF_RELEASE = "14-Oct-2022"

EASYCHAT_DOMAIN = "easychat-dev.allincall.in"

EASYCHAT_HOST_URL = "https://" + EASYCHAT_DOMAIN

ALLOWED_HOSTS = [EASYCHAT_DOMAIN, "127.0.0.1", "0.0.0.0"]

MASKING_PII_DATA_OTP_EMAIL = ['aman@getcogno.ai', 'harshita@getcogno.ai']

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

CSRF_FAILURE_VIEW = 'EasyChatApp.views.csrf_failure'

CRONJOB_REPORT_EMAIL = [
    'nayan.jain@getcogno.ai',
]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
    BASE_DIR, 'google_translate_api.json')

# ALLOWED_HOSTS = ["*"]

if DEBUG == False:

    # X_FRAME_OPTIONS = 'DENY'
    # setting X_FRAME_OPTIONS to 'ALLOWALL' for Salesforce Integration
    X_FRAME_OPTIONS = 'ALLOWALL'

    # X_FRAME_OPTIONS = 'SAMEORIGIN'

    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET']

    if EASYCHAT_DOMAIN in ["easychat-dev.allincall.in", "easychat-uat.allincall.in", "easychat.allincall.in", "easychat-stag.allincall.in"]:

        CORS_ORIGIN_ALLOW_ALL = True

        CORS_ORIGIN_WHITELIST = [EASYCHAT_HOST_URL, "https://accounts.google.com"]

        CORS_ALLOW_METHODS = ['GET', 'POST']

        EASYCHAT_SHOW_CONSOLE_LOGS = True

    else:

        CORS_ORIGIN_ALLOW_ALL = False

        CORS_ORIGIN_WHITELIST = [EASYCHAT_HOST_URL]

        CORS_ALLOW_METHODS = ['GET', 'POST']

        EASYCHAT_SHOW_CONSOLE_LOGS = False

    BLOCKED_URLPATTERNS = ["/admin"]

    CSRF_COOKIE_SECURE = True

    CSRF_COOKIE_HTTPONLY = True

    CSRF_COOKIE_DOMAIN = EASYCHAT_DOMAIN

    CSRF_COOKIE_AGE = 1800  # 30 minutes

    SESSION_COOKIE_SECURE = True

    SESSION_COOKIE_DOMAIN = EASYCHAT_DOMAIN

    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    ENABLE_IP_TRACKING = True

    CONFIG_FILE = open(os.path.join(BASE_DIR, 'files/') + "livechat_integrations/config.json", 'r')

    JSON_DATA = json.load(CONFIG_FILE)

    if JSON_DATA['ms_dynamics']['is_integrated']:
        CSRF_COOKIE_HTTPONLY = False
        CSRF_COOKIE_SAMESITE = 'None'
        CSRF_TRUSTED_ORIGINS = JSON_DATA['ms_dynamics']['CSRF_TRUSTED_ORIGINS']
        CSRF_TRUSTED_ORIGINS.append(EASYCHAT_DOMAIN)
        SESSION_SAVE_EVERY_REQUEST = True
        SESSION_COOKIE_SAMESITE = 'None'
        SESSION_COOKIE_HTTPONLY = False

else:

    CORS_ORIGIN_ALLOW_ALL = True

    ENABLE_IP_TRACKING = False

    X_FRAME_OPTIONS = 'ALLOWALL'

    BLOCKED_URLPATTERNS = []

    CRONJOB_REPORT_EMAIL = []

    EASYCHAT_SHOW_CONSOLE_LOGS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-AccessToken'
]

# SESSION_COOKIE_AGE = 600

EASYCHAT_SESSION_AGE = 1200  # 20 min inactivity

ENABLE_AUTO_LOGOUT_SESSION = True

# SESSION_EXPIRE_SECONDS = EASYCHAT_SESSION_AGE

# SESSION_TIMEOUT_REDIRECT = EASYCHAT_HOST_URL + "/chat/logout/"

# SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

WHITELISTED_IP_ADDRESSES = []  # We do not use this variable to whitelist ip addresses anymore. You can add ip addresses in DeveloperConsoleConfig table's whitelisted_ip_addresses column from django admin to whitelist ip address.

WHITELISTED_URLPATTERNS = []

WHITELISTED_IP_FOR_BLOCKED_URLS = ['65.2.65.107']

# Time interval to update bot suggestion list
UPDATE_SUGGESTION_LIST_FREQUENCY = 300

# Cobrowsing App Settings

WRONG_PASSWORD_LOCKIN_TIMEOUT = 600  # mins

WRONG_PASSWORD_ATTEMPTS = 5

EASYCHAT_PROCESSORS_MAX_RUNTIME_LIMIT = 5  # time interval in seconds after which processors execution is stoped

ALLOW_SIMULTANEOUS_LOGIN = False

EASYASSIST_HOST_PROTOCOL = "https"

EASYASSISTAPP_HOST = EASYCHAT_HOST_URL

EASYASSISTSALESFOCEAPP_HOST = EASYCHAT_HOST_URL

EASYCHAT_ADMIN_USER = ["shreyas@getcogno.ai",
                       "harshita@getcogno.ai", "aman@getcogno.ai"]

PARAPHRASE_NLP_CORE = "en_core_web_sm"

SECURE_BROWSER_XSS_FILTER = True

QUERY_API_TIMEOUT = 30  # For automated flow testing platform

DEVELOPMENT = DEBUG

CACHE_TIME = 86400

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'EasyChatApp',
    'rest_framework',
    'corsheaders',
    'oauth2_provider',
    'django_ace',
    'logtailer',
    'channels',
    'EasySearchApp',
    'EasyTMSApp',
    'LiveChatApp',
    'EasyAssistApp',
    'AutomatedAPIApp',
    'AuditTrailApp',
    'CampaignApp',
    'DeveloperConsoleApp',
    'django_saml2_auth',
    'django_crontab',
    'EasyAssistSalesforceApp',
    'TestingApp',
    'OAuthApp',
    'CognoMeetApp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'EasyChatApp.middleware.IPAddressCheckMiddleware',
    'EasyChatApp.middleware.AutoLogout',
]


ROOT_URLCONF = 'EasyChat.urls'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'EasyChatApp.context_processors.is_console_logs',
                'DeveloperConsoleApp.context_processors.get_livechat_config_obj',
                'DeveloperConsoleApp.context_processors.get_easychat_config_obj',
                'DeveloperConsoleApp.context_processors.get_developer_console_config_obj',
                'DeveloperConsoleApp.context_processors.get_cognodesk_console_config_obj',
                'DeveloperConsoleApp.context_processors.get_cobrowse_console_config_obj',
                'DeveloperConsoleApp.context_processors.get_cognomeet_console_config_obj',
            ],
            'builtins': [
                'LiveChatApp.templatetags.random_numbers',
            ],
        },
    },
]

WSGI_APPLICATION = 'EasyChat.wsgi.application'

AUTH_USER_MODEL = "EasyChatApp.User"

KAFKA_CONFIG = {
    # 'bootstrap_servers': '43.205.202.74:9092',
    'bootstrap_servers': 'ip-172-31-7-78:9092',
    'livechat_report_topic': 'LiveChatReportTopic',
}


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if DEBUG:
    # Sqlite Database Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

else:
    # Postgres Database Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'easychat_db_4',
            'USER': 'easychat_allincall',
            'PASSWORD': 'AllinCall@123$',
            'HOST': '172.31.8.161',
            'PORT': '',
            # 'NAME': 'ecs_test_12_05_2022',
            # 'USER': 'ecs_test_user',
            # 'PASSWORD': 'ecs1234',
            # 'HOST': '172.31.21.113',
            # 'PORT': '',
        }
    }


"""
# MySQL Database Configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'your_host_address',
        'PORT': 'your_port',
    }
}
"""

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/EasyChatCache',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

"""
EasyChat Sensitive Tag
"""

EASYCHAT_SENSITIVE_REGEX = r"(<easychat:sensitive>)(.*?)(<\/easychat:sensitive>)"

EASYCHAT_LEMMATIZER_REQUIRED = True

EASYCHAT_DEFAULT_CHAT_PAGE = "EasyChatApp/theme2.html"

EASYCHAT_DEFAULT_MAIN_PAGE = "EasyChatApp/theme2_bot.html"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_ROOT = os.path.join(BASE_DIR, 'files/')

SECURE_MEDIA_ROOT = os.path.join(BASE_DIR, 'secured_files/')

MEDIA_URL = '/files/'

IMAGE_UPLOAD_PATH = "images"

EASYCHAT_ROOT = os.path.join(BASE_DIR, 'EasyChat/')

LIVECHAT_ROOT = os.path.join(BASE_DIR, 'LiveChatApp/')

EASYCHAT_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'EasyChatApp/')

ELASTIC_SEARCH_OBJ = Elasticsearch(['https://elasticsearch.allincall.in:443/'], http_auth=('elastic', 'AllinCall@123'))

if DEBUG:
    ELASTIC_SEARCH_OBJ = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}], verify_certs=True)    

APP_LOG_FILENAME = os.path.join(BASE_DIR, 'log/app.log')

ERROR_LOG_FILENAME = os.path.join(BASE_DIR, 'log/error.log')

SENSITIVE_LOG_FILENAME = os.path.join(BASE_DIR, 'log/sensitive.log')

LOGFILE_SIZE = 20 * 1024 * 1024

LOGFILE_COUNT = 5

LOGFILE_APP = 'EasyChatApp'

CAMPAIGNAPP_LOGFILE = 'CampaignApp'

DEVELOPER_CONSOLE_APP_LOGFILE = 'DeveloperConsoleApp'

EASYSEARCHAPP_LOGFILE = 'EasySearchApp'

EASYTMSAPP_LOGFILE = 'EasyTMSApp'

LIVECHATAPP_LOGFILE = "LiveChatApp"

EASYASSISTAPP_LOGFILE = "EasyAssistApp"

COGNOMEETAPP_LOGFILE = "CognoMeetApp"

EASYASSISTSALESFORCEAPP_LOGFILE = 'EasyAssistSalesforceApp'

AUTOMATEDAPIINTEGRATION_LOGFILE = 'AutomatedAPIApp'

TESTINAPP_LOGFILE = 'TestingApp'

AUDITTRAILAPP_LOGFILE = 'AuditTrailApp'

OAUTHAPP_LOGFILE = 'OAuthApp'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'easychat_standard': {
            'format': "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] [%(AppName)s] [%(channel)s] [%(bot_id)s] %(message)s",
            'datefmt': "%d-%b-%Y %H:%M:%S"
        },
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] [%(AppName)s] %(message)s",
            'datefmt': "%d-%b-%Y %H:%M:%S"
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'custom_filter': {
            '()': 'EasyChatApp.log_filter.SensitiveDataFilter'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
        'mail_admins': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'easychat_applog': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': APP_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'easychat_standard',
        },
        'easychat_errorlog': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'easychat_standard',
        },
        'easychat_sensitivelog': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SENSITIVE_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'easychat_standard',
            'filters': ['custom_filter']
        },
        'applog': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': APP_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'standard',
        },
        'errorlog': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'standard',
        },
        'sensitivelog': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SENSITIVE_LOG_FILENAME,
            'maxBytes': LOGFILE_SIZE,
            'backupCount': LOGFILE_COUNT,
            'formatter': 'standard',
            'filters': ['custom_filter']
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        LOGFILE_APP: {
            'handlers': ['easychat_applog', 'easychat_errorlog', 'easychat_sensitivelog'],
            'level': 'INFO',
            'propagate': True,
        },
        CAMPAIGNAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        DEVELOPER_CONSOLE_APP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        EASYSEARCHAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        EASYTMSAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        LIVECHATAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        EASYASSISTAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        COGNOMEETAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        EASYASSISTSALESFORCEAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        AUTOMATEDAPIINTEGRATION_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        TESTINAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        AUDITTRAILAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        },
        OAUTHAPP_LOGFILE: {
            'handlers': ['applog', 'errorlog'],
            'level': 'INFO',
            'propagate': True,
        }

    }
}

LOGTAILER_HISTORY_LINES = 50

LOGTAILER_LINES = 1000

GOOGLE_SEARCH_DEVELOPER_KEY = "AIzaSyDlwlpT2vTVkYVmdmALdSJ12RC3Ex3PZxQ"

GOOGLE_SEARCH_CUSTOM_SEARCH_KEY = "009085939227162172546:d5vguy3w0ey"

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# LiveChat Requirements
ASGI_APPLICATION = 'EasyChat.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('172.31.8.161', 6379)],
            "capacity": 1500,
            "expiry": 10
        },
    },
}

# Maximum size of POST request is currently 10MB.

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = 'success@allincall.in'

EMAIL_HOST_PASSWORD = 'xtjnoekylhmdgrvx'

EMAIL_CSM = 'csm@allincall.in'

EMAIL_NOTIFICATIONS = 'allincall.notifications@gmail.com'

SAML2_AUTH = {
    # Metadata is required, choose either remote url or local file path
    'METADATA_AUTO_CONF_URL': '[The auto(dynamic) metadata configuration URL of SAML2]',
    'METADATA_LOCAL_FILE_PATH': os.path.join(BASE_DIR, 'google-ldap.conf'),
    # Optional settings below
    # Custom target redirect URL after the user get logged in. Default to
    # /admin if not set. This setting will be overwritten if you have
    # parameter ?next= specificed in the login URL.
    'DEFAULT_NEXT_URL': '/chat/home',
    # Create a new Django user when a new user logs in. Defaults to True.
    'CREATE_USER': 'TRUE',
    'NEW_USER_PROFILE': {
        'USER_GROUPS': [],  # The default group name when a new user logs in
        'ACTIVE_STATUS': True,  # The default active status for new users
        'STAFF_STATUS': True,  # The staff status for new users
        'SUPERUSER_STATUS': False,  # The superuser status for new users
    },
    'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
        'email': 'EmailID',
        'username': 'EmailID',
        'first_name': 'FirstName',
        'last_name': 'LastName',
    },
    'TRIGGER': {
        'CREATE_USER': 'EasyChatApp.utils.sso_pre_login_check',
        'BEFORE_LOGIN': 'EasyChatApp.utils.sso_pre_login_check',
    },
    # Custom URL to validate incoming SAML requests against
    'ASSERTION_URL': EASYCHAT_HOST_URL,
    # Populates the Issuer element in authn request
    'ENTITY_ID': EASYCHAT_HOST_URL + '/sso_auth/acs/',
    'NAME_ID_FORMAT': "None",  # Sets the Format property of authn NameIDPolicy element
    # Set this to True if you are running a Single Page Application (SPA) with
    # Django Rest Framework (DRF), and are using JWT authentication to
    # authorize client users
    'USE_JWT': False,
    # Redirect URL for the client if you are using JWT auth with DRF. See
    # explanation below
    'FRONTEND_URL': EASYCHAT_HOST_URL,
}

IS_REPORT_GENERATION_VIA_KAFKA_ENABLED = True

########################      CRONJOB     ######################

CRONJOBS = [
    # ('* * * * *', 'cronjob_scripts.test_cronjob.cronjob'),
    # comment the first and second cronjobs incase facing load on server
    ('*/5 * * * *', 'cronjob_scripts.csat_whatsapp.cronjob'),
    ('*/5 * * * *', 'cronjob_scripts.csat_viber.cronjob'),
    ('* * * * *', 'cronjob_scripts.whatsapp_campaign_trigger_cronjob.cronjob'),
    # ('* * * * *', 'cronjob_scripts.rcs_campaign_trigger_cronjob.cronjob'),
    ('0 19 * * *', 'cronjob_scripts.livechat_combined_cronjob.cronjob'),
    ('30 0 * * *', 'cronjob_scripts.easychat_combined_cronjob.cronjob'),
    ('0 * * * *', 'cronjob_scripts.check_bot_usage_analytics.cronjob'),
    ('*/5 * * * *', 'cronjob_scripts.session_timeout.cronjob'),
    ('0 23 * * *', 'cronjob_scripts.easyassist_combined_cronjob.cronjob'),
    ('0 20 * * *', 'cronjob_scripts.tms_analytics_cronjob.cronjob'),
    ('30 20 * * *', 'cronjob_scripts.audit_trail_app_cronjob.cronjob'),
    ('0 * * * *', 'cronjob_scripts.easyassist_mask_customer_details_cronjob.cronjob'),
    ('0 10 * * *', 'cronjob_scripts.unanswered_periodic_cronjob.unanswered_queries_cronjob'),
    ('0 14 * * *', 'cronjob_scripts.unanswered_periodic_cronjob.unanswered_queries_cronjob'),
    ('0 17 * * *', 'cronjob_scripts.unanswered_periodic_cronjob.unanswered_queries_cronjob'),
    ('0 * * * *', 'cronjob_scripts.misdashboard_today_cronjob.cronjob'),
    ('0 */6 * * *', 'cronjob_scripts.campaign_export.cronjob'),
    ('0 */12 * * *', 'cronjob_scripts.pdf_search_export.cronjob'),
    ('0 22 * * *', 'cronjob_scripts.livechat_send_mail_analytics.cronjob'),
    # ('*/2 * * * *', 'cronjob_scripts.gbm_survey_cronjob.check_and_send_gbm_survey'),
    ('0 23 * * *', 'cronjob_scripts.send_easychat_analytics_mail.cronjob'),
    ('* * * * *', 'cronjob_scripts.update_voice_bot_campaign_details.cronjob'),
    ('* * * * *', 'cronjob_scripts.update_call_details.cronjob'),
    ('30 22 * * *', 'cronjob_scripts.export_voice_campaign_history_data.cronjob'),
    ('30 22 * * *', 'cronjob_scripts.export_whatsapp_campaign_history_data.cronjob'),
    # ('*/5 * * * *', 'cronjob_scripts.cognomeet_archive_meeting_sessions.cronjob'),
    # ('0 3 * * *', 'cronjob_scripts.cognomeet_fetch_meeting_recordings.cronjob'),
    # ('0 * * * *', 'cronjob_scripts.cognomeet_combined_cronjob.cronjob'),
]
