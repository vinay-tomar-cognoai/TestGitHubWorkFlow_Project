from django.db import models
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings
from django.core.cache import cache
from slugify import slugify
from oauth2_provider.models import AccessToken
from django.utils.safestring import mark_safe
from functools import reduce
from bs4 import BeautifulSoup

import ast
import sys
import json
import uuid
import logging  # noqa: F401
import hashlib
import re

from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_models import get_fifteen_days_from_now, get_default_intent_icon, get_user_query_pos_list, get_training_dict_with_pos, sync_tree_object_training_data
from EasyChatApp.utils_sentiment_analysis import *
from EasyChatApp.constants_mailer_analytics import *
from EasyChatApp.constants import DEFAULT_LEAD_TABLE_COL, LIVECHAT_PROVIDERS, DEFAULT_LIVECHAT_PROVIDER, BLOCK_TYPE_CHOICES
from LiveChatApp.utils import DecryptVariable
from EasyChatApp.utils_custom_encryption import CustomEncrypt

from EasyChatApp.log_filter import *

from EasyChatApp.cryptography import *

from EasyTMSApp.models import Agent, TicketCategory

from EasyAssistApp.models import CobrowseAgent, CobrowsingAuditTrail, CobrowsingFileAccessManagement, CobrowseSandboxUser

from TestingApp.models import Tester, BotQATesting

from EasyChatApp.constants_catalogue import *

logger = logging.getLogger(__name__)


class EasyChatAccessToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique access token key')

    timestamp = models.DateTimeField(default=timezone.now)

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'EasyChatAccessToken'
        verbose_name_plural = 'EasyChatAccessToken'


class EasyChatQueryToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique access token key')

    timestamp = models.DateTimeField(default=timezone.now)

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'EasyChatQueryToken'
        verbose_name_plural = 'EasyChatQueryToken'


class NPS(models.Model):
    channel = models.ManyToManyField(
        'EasyChatApp.Channel', blank=True, help_text='Selected channels have NPS allowed')

    bot = models.OneToOneField('EasyChatApp.Bot', null=True,
                               blank=True, help_text="Selected bot have NPS allowed", on_delete=models.SET_NULL,)

    whatsapp_nps_time = models.IntegerField(
        default=2, null=True, blank=True, help_text="NPS time out for WhatsApp (in minutes)")

    viber_nps_time = models.IntegerField(
        default=2, null=True, blank=True, help_text="NPS time out for Viber (in minutes)")

    csat_reset_duration = models.IntegerField(
        default=1, null=True, blank=True, help_text="CSAT reset duration (in days)")

    def __str__(self):
        try:
            return str(self.bot.name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("NPS %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
            return "Error"

    class Meta:
        verbose_name = 'NPS'
        verbose_name_plural = 'NPS'


class SandboxUser(models.Model):
    username = models.CharField(max_length=256,
                                null=False,
                                blank=False,
                                help_text='Username of SandboxUser')
    password = models.CharField(max_length=256,
                                null=True,
                                blank=True,
                                help_text='Password of SandboxUser')
    created_on = models.DateTimeField(
        default=timezone.now, help_text="Datetime when the user Credentials are created")

    will_expire_on = models.DateTimeField(default=get_fifteen_days_from_now, null=False,
                                          blank=False, help_text="Datetime when the user Credentials will expire")

    is_expired = models.BooleanField(default=False, null=False, blank=False,
                                     help_text="designates wheter the credentials are expired or not")

    last_extention_date = models.DateTimeField(null=True,
                                               blank=True,
                                               help_text='when was the last extention done')
    number_of_times_extended = models.IntegerField(default=0, null=True,
                                                   blank=True, help_text="count of total extentions made")

    def __str__(self):
        return str(self.username)


class User(AbstractUser):

    role = models.CharField(max_length=256,
                            null=False,
                            blank=False,
                            choices=USER_CHOICES,
                            help_text='Role of a user where user can be "bot_builder" or "customer_care_agent".')
    status = models.CharField(max_length=1,
                              null=True,
                              blank=True,
                              choices=ROLES,
                              help_text='Status is for EasyTMS where user can be "Manager" or "Agent".')

    is_online = models.BooleanField(
        default=False, help_text="Designates whether the user is online or not. It helps to prevent simultaneous login of same user.")

    package_reviewer = models.BooleanField(
        default=False, help_text='User who is allow to review the package installation request and approve')

    is_general_feedback_page_access_allowed = models.BooleanField(
        default=False)

    is_chatbot_creation_allowed = models.CharField(
        max_length=1,
        default='3',
        choices=BOT_CREATION_PERMISSION)

    is_bot_invocation_enabled = models.BooleanField(
        default=False, help_text="Let users invoke your bot")

    is_first_login = models.BooleanField(
        default=False, help_text="Force to change password on first login")

    websocket_token = models.CharField(
        max_length=100, help_text='unique websocket token key', null=True, blank=True)

    password_change_duration = models.CharField(
        max_length=256, null=True, blank=True, choices=PASSWORD_RESET_DURATION, help_text="Forcing user to change password after this duartion")

    sandbox_users = models.ManyToManyField(
        SandboxUser, blank=True, related_name="sandboxuser", help_text="sandboxuser")

    is_guest = models.BooleanField(default=False)
    is_sandbox_user = models.BooleanField(default=False)
    enable_s3_bucket = models.BooleanField(default=True)
    enable_white_label_option = models.BooleanField(default=False)

    def name(self):
        return self.first_name + ' ' + self.last_name

    def clean(self, *args, **kwargs):
        username = self.username
        email_regex = '^[a-zA-Z0-9][a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$'
        if(not re.search(email_regex, username)):
            raise ValidationError("Username should be a valid email id")

        if not self.password.startswith("pbkdf2_sha256$260000$"):
            password_regex = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,32}$'
            if(not re.match(password_regex, self.password)):
                raise ValidationError(mark_safe("The password isn't strong enough.\
                                        <br>Please make sure it has:\
                                        <br>1. At least one digit [0-9]\
                                        <br>2. At least one lowercase character [a-z]\
                                        <br>3. At least one uppercase character [A-Z]\
                                        <br>4. At least one special character [*.!@#$%^&(){}[]:;<>,.?/~_+-=|\]\
                                        <br>5. At least 8 characters in length, but no more than 32."))
        super(User, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk == None:
            self.set_password(self.password)
        elif not self.password.startswith("pbkdf2_sha256$260000$"):
            self.set_password(self.password)

        if self.email.lower() in ["shreyas@getcogno.ai", "harshita@getcogno.ai", "aman@getcogno.ai"]:
            self.superuser_status = True
            self.is_superuser = True

        try:
            if self.username.lower().split("@")[-1] == "getcogno.ai" and self.is_chatbot_creation_allowed == '3':
                self.is_chatbot_creation_allowed = "1"
        except Exception:
            pass

        try:
            if self.email.lower().split("@")[-1] == "getcogno.ai":
                self.role = "bot_builder"
                self.status = "1"
        except Exception:
            pass

        self.websocket_token = self.username

        super(User, self).save(*args, **kwargs)

    def get_related_bot_objs(self):
        bot_objs = Bot.objects.filter(
            users__in=[self], is_uat=True, is_deleted=False).distinct()
        return bot_objs

    def get_bot_related_access_perm(self, bot_pk=None):
        if bot_pk is not None:
            bot_objs = Bot.objects.filter(pk=bot_pk, is_deleted=False)
        else:
            bot_objs = get_related_bot_objs(self)
        access_dict = {}
        for bot_obj in bot_objs:
            access_dict[bot_obj.pk] = bot_obj.is_accessible(self)
        return access_dict

    def get_bot_related_type_access(self, bot_pk=None):
        if bot_pk is not None:
            bot_objs = Bot.objects.filter(pk=bot_pk, is_deleted=False)
        else:
            bot_objs = get_related_bot_objs(self)
        access_dict = {}
        for bot_obj in bot_objs:
            bot_obj_accesses = set(bot_obj.is_accessible(self))
            bot_obj_access_list = []

            if set(["Full Access", "Intent Related", "Categories", "Extract FAQ Related", "Create Bot With Excel Related", "Word Mapper Related", "Bot Setting Related", "PDF Searcher"]).intersection(bot_obj_accesses):
                bot_obj_access_list.append("build_bot")

            if set(["Full Access", "Bot Setting Related"]).intersection(bot_obj_accesses):
                bot_obj_access_list.append("configure_bot")

            if set(["Full Access", "Automated Testing", "Bot Setting Related"]).intersection(bot_obj_accesses):
                bot_obj_access_list.append("test_and_deploy")

            if set(["Full Access", "Analytics Related", "Conversion Analytics Related", "API Analytics Related", "Message History Related", "Self Learning Related"]).intersection(bot_obj_accesses):
                bot_obj_access_list.append("analyze_and_improve")

            if set(["Full Access", "Form Assist Related", "Lead Gen Related", ]).intersection(bot_obj_accesses):
                bot_obj_access_list.append("additional_tools")

            access_dict[bot_obj.pk] = bot_obj_access_list
        return access_dict

    def get_overall_access_perm(self, bot_pk=None):
        if bot_pk is not None:
            bot_objs = Bot.objects.filter(pk=bot_pk, is_deleted=False)
        else:
            bot_objs = get_related_bot_objs(self)
        access_array = []
        for bot_obj in bot_objs:
            access_array += bot_obj.is_accessible(self)
        return list(set(access_array))

    def get_related_bot_objs_for_access_type(self, access_type):
        try:
            full_access_obj = AccessType.objects.get(name="Full Access")
            access_type_obj = AccessType.objects.get(name=access_type)
            bot_objs = []
            for access_manage_obj in AccessManagement.objects.filter(
                    user=self, bot__is_deleted=False, access_type__in=[access_type_obj, full_access_obj]):
                bot_objs += [access_manage_obj.bot]
            return bot_objs
        except Exception:
            return []

    def check_data_collection_permission(self):
        try:
            return Config.objects.all()[0].is_data_collection_on
        except Exception:
            return False

    def check_data_drive_permission(self):
        try:
            return Config.objects.all()[0].is_data_drive_on
        except Exception:
            return False

    def check_feedback_permission(self):
        try:
            return Config.objects.all()[0].is_feedback_on
        except Exception:
            return False

    def check_sso_permission(self):
        try:
            return Config.objects.all()[0].is_sso_on
        except Exception:
            return False

    def get_ms_integration_url(self):
        try:
            with open(f'{settings.MEDIA_ROOT}livechat_integrations/config.json', 'r') as config_file:
                data = json.load(config_file)

                if data['ms_dynamics']['is_integrated']:
                    url = data['ms_dynamics']['CSRF_TRUSTED_ORIGINS']

                    if len(url) != 0:
                        url = url[0]

                        if url[-1] != '/':
                            url += '/'

                        return url
                    else:
                        return ""

                return ""
        except Exception:
            return ""

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


def get_related_bot_objs(self):
    bot_objs = Bot.objects.filter(users__in=[self], is_uat=True, is_deleted=False).distinct()
    return bot_objs


auth.models.User.add_to_class('get_related_bot_objs', get_related_bot_objs)


@receiver(post_save, sender=User)
def create_supervisor(sender, instance, **kwargs):
    if instance.is_staff:
        if len(Supervisor.objects.filter(supervisor=instance)) == 0:
            Supervisor.objects.create(supervisor=instance)

    if instance.role == CUSTOMER_CARE_AGENT_ROLE:
        if len(CustomerCareAgent.objects.filter(user=instance)) == 0:
            CustomerCareAgent.objects.create(user=instance)

    if len(SecuredLogin.objects.filter(user=instance)) == 0:
        SecuredLogin.objects.create(user=instance)

    if Tester.objects.filter(user=instance).count() == 0:
        Tester.objects.create(user=instance)


class DuplicateIntentExceptionError(Exception):
    pass


class IntentAuthenticationTypeExceptionError(Exception):
    pass


class Profile(models.Model):

    bot = models.ForeignKey(
        'Bot', null=True, blank=True, on_delete=models.SET_NULL)

    user_id = models.CharField(
        max_length=100, db_index=True, help_text="Unique user id.")

    user_pipe = models.TextField(
        default="", help_text="Store the conversation of user and bot in pipe seperated format.")

    tree = models.ForeignKey(
        'Tree', null=True, blank=True, on_delete=models.SET_NULL)

    previous_tree = models.ForeignKey(
        'Tree', null=True, blank=True, related_name='previous_tree', on_delete=models.SET_NULL)

    previous_data = models.TextField(
        default="{}", help_text="Previous data of the user.")

    channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)

    livechat_connected = models.BooleanField(default=False)

    livechat_session_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="livechat session id for WhatsApp channel")

    last_message_date = models.DateTimeField(default=timezone.now)

    previous_message_date = models.DateTimeField(null=True, blank=True)

    is_nps_message_send = models.BooleanField(default=False)

    is_comment_needed = models.BooleanField(default=False)

    selected_language = models.ForeignKey(
        'Language', null=True, blank=True, on_delete=models.SET_NULL, help_text="Language selected by user (in whatsapp)")

    campaign_optin = models.BooleanField(
        default=False, help_text='Designates whether user has opted in campaign or not.')

    is_csat_triggers = models.BooleanField(default=False)

    last_csat_triggered_date = models.DateTimeField(default=timezone.now)

    is_csat_submited = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.user_id

    def is_user_authenticated(self, identified_intent, channel_obj, src, bot_id):
        try:
            identified_tree = identified_intent.tree

            authetication_type = identified_intent.auth_type.name
            channel_name = channel_obj.name

            # authentication_obj = Authentication.objects.get(
            #     name=authetication_type)
            authentication_obj = Authentication.objects.filter(
                name=authetication_type).order_by('-pk')[0]

            authentication_tree = authentication_obj.tree

            user_authentication_obj = None
            try:
                user_authentication_obj = UserAuthentication.objects.get(
                    user=self, auth_type=authentication_obj)
            except Exception:  # noqa: F841
                pass

            if channel_name == "Web" or channel_name == "WhatsApp" or channel_name == "Android" or channel_name == "GoogleRCS" or channel_name == "GoogleBusinessMessages":

                if user_authentication_obj == None:
                    return False, authentication_tree

                import pytz
                tz = pytz.timezone(settings.TIME_ZONE)
                auth_datetime_obj = user_authentication_obj.start_time.astimezone(
                    tz)
                current_datetime_obj = timezone.now().astimezone(tz)

                if (current_datetime_obj - auth_datetime_obj).total_seconds() <= int(authentication_obj.auth_time):
                    return True, identified_tree

                return False, authentication_tree

            elif channel_name == "GoogleHome" or channel_name == "Alexa":

                if user_authentication_obj == None:
                    return False, None

                user_params = json.loads(user_authentication_obj.user_params)
                if "AccessToken" in user_params:
                    if user_params["AccessToken"] != None:
                        return True, identified_tree

                return False, None

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("is_user_authenticated %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                self.user_id), 'source': str(src), 'channel': str(channel_name), 'bot_id': str(bot_id)})

        return False, None


class Channel(models.Model):

    name = models.CharField(max_length=100, null=False,
                            help_text="Channel name")

    icon = models.TextField(default="", help_text="svg code for channel icon.")

    is_easychat_channel = models.BooleanField(
        default=True, help_text="Designates whether this channel is available for easychat.")

    class Meta:
        verbose_name = "Channel"
        verbose_name_plural = "Channels"

    def __str__(self):
        return self.name


class WordMapper(models.Model):

    keyword = models.CharField(max_length=100, help_text="Keyword")

    similar_words = models.TextField(
        null=False, help_text="Similar words for given keyword")

    bots = models.ManyToManyField(
        'Bot', blank=True, help_text="Bots for which word mapper has been added")

    synced = models.BooleanField(
        default=False, help_text="Designates whether it is synced with intent or not.")

    def get_similar_word_list(self):
        similar_words = [
            word for word in self.similar_words.split(",") if word != ""]
        return similar_words

    def __str__(self):

        return self.keyword + ": " + self.similar_words


class BotInfo(models.Model):

    bot = models.ForeignKey(
        'Bot', blank=True, null=True, on_delete=models.SET_NULL, help_text="Bot Object whose info stored")

    activity_update = models.TextField(
        default="{}", help_text="Stores information wheter a particular field is edited or not")

    bad_keywords = models.TextField(
        default="[]", blank=True, null=True, help_text="list of bad words")

    is_suggested_intent_learning_on = models.BooleanField(
        default=True, help_text="when true the bot will learn based on suggestions")

    suggested_intent_selected_threshold = models.IntegerField(
        default=10, help_text="Threshold value after which a selected intent is learned by bot ")

    is_trigger_livechat_enabled = models.BooleanField(
        default=False, help_text="livechat suggestion will be triggered on true")

    is_percentage_match_enabled = models.BooleanField(
        default=True, help_text="Message history will show % match and variation responsible if triggered")

    autosuggest_livechat_word_limit = models.IntegerField(
        default=30, help_text="The word count limit after which livechat suggestion will be triggered")

    static_conversion_analytics = models.BooleanField(
        default=False, help_text='show static conversion analytics for demo')

    console_meta_data = models.TextField(default=json.dumps(
        {"lead_data_cols": DEFAULT_LEAD_TABLE_COL}), null=True, blank=True)

    threshold_confidence_for_language_detection = models.FloatField(
        default=0.75, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text="Confidence Threshold value for Language Detection between 0 to 1")

    is_bot_chat_history_to_be_shown_on_refresh = models.BooleanField(
        default=True, help_text='when user in same session closes the tab or refreshes the page wheter to show easychat bot chat history or not')

    enable_flagged_queries_status = models.BooleanField(
        default=True, help_text="If this is enabled then False Positives and Not False Positives column will be enabled and analytical view will also be enabled.")

    enable_intent_icon = models.BooleanField(
        default=True, help_text="If this is enabled then recommended intents in chatbot will appear as intent names with intent icons.")

    enable_spell_check_while_typing = models.BooleanField(
        default=False, help_text="If this is enabled then spell check logic while typing will be enabled in frontend.")

    enable_abort_flow_feature = models.BooleanField(
        default=True, help_text="Enabling this will display a message in case when a user invokes an intent/training question in the middle of a current flow.")

    is_bot_break_email_notification_enabled = models.BooleanField(
        default=True, help_text="Is email notifications on Bot break enabled on this bot")

    bot_break_mail_sender_time_interval = models.IntegerField(
        default=1, null=True, blank=True, help_text='The time interval between two mail sent for same Bot Break in minutes.')

    bot_break_mail_sent_to_list = models.TextField(
        default="{\"items\":[\"csm@getcogno.ai\"]}", blank=True, help_text='The list of user to whom the mail needs to be sent.')

    is_advance_tree_level_nlp_enabled = models.BooleanField(
        default=False, help_text="Currently this toggle designates whether semantic similarity should be enabled for tree recogniztion or not")

    child_trees_similarity_threshold = models.FloatField(
        default=0.7, help_text="This threshold is used to identify child tree based on similarity with the user sentence.")

    repeat_variation_similarity_threshold = models.FloatField(
        default=0.6, help_text="This threshold is used for voice bot to match the sentence with repeat variation.")

    custom_intents_for = models.CharField(max_length=256, default=AUTO_POPUP, null=False, blank=False, choices=CUSTOM_INTENTS_CHOICE,
                                          help_text='Designates whether custom intents are of form assist or auto popup or etc')

    enable_custom_intent_bubbles = models.BooleanField(
        default=False, help_text="If this is enabled then custom intent bubbles for webpages can be assigned.")
    
    exclude_intuitive_query_from_bot_accuracy = models.BooleanField(
        default=True, help_text="If this is enabled then intuitive query will not be considered for bot accuracy.")

    livechat_provider = models.CharField(
        max_length=50, default=DEFAULT_LIVECHAT_PROVIDER, null=False, blank=False, choices=LIVECHAT_PROVIDERS)

    show_welcome_msg_on_end_chat = models.BooleanField(
        default=True, help_text="If this is enabled then welcome message is displayed on end chat")

    enable_do_not_translate = models.BooleanField(default=False, help_text="If this is enabled then matching words in do_not_translate_keywords_list and will not be translated")

    do_not_translate_keywords_list = models.TextField(default=json.dumps(DEFAULT_DO_NOT_TRANSLATE_KEYWORDS), null=True, blank=True, help_text="This field is used to store words which should not be translated.")

    do_not_translate_regex_list = models.TextField(default="[]", null=True, blank=True, help_text="This field is used to store the regex which should not be translated.")

    intent_icon_channel_choices_info = models.TextField(default=json.dumps(DEFAULT_INTENT_ICON_CHANNEL_CHOICES_INFO), null=True, blank=True, help_text="This field is used to store the information realted to displaying of intent icons.")

    is_geolocation_enabled = models.BooleanField(
        default=True, help_text="If this is enabled then location will be requested from user when bot is opened")

    class Meta:
        verbose_name = "BotInfo"
        verbose_name_plural = "BotInfo"

    def __str__(self):
        return str(self.bot.name)

    def get_do_not_translate_keywords_list(self):
        try:
            if self.do_not_translate_keywords_list:
                return json.loads(self.do_not_translate_keywords_list)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_do_not_translate_keywords_list %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []

    def get_do_not_translate_regex_list(self):
        try:
            if self.do_not_translate_regex_list:
                return json.loads(self.do_not_translate_regex_list)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_do_not_translate_regex_list %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []

    def get_intent_icon_channel_choices_info(self):
        try:
            if self.intent_icon_channel_choices_info:
                return json.loads(self.intent_icon_channel_choices_info)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_intent_icon_channel_choices_info %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return {}


class FormAssistBotData(models.Model):

    bot = models.ForeignKey(
        'Bot', blank=True, null=True, on_delete=models.CASCADE, help_text="Bot Object whose form assist info is stored")

    form_assist_auto_popup_type = models.CharField(
        default="1", help_text='Designates form assist popup type for the bot.', max_length=20)

    form_assist_autopop_up_timer = models.IntegerField(
        default=10, help_text='Form assist autobot popup timer.')

    form_assist_autopop_up_inactivity_timer = models.IntegerField(
        default=5, help_text='User Inactivity timer during form assist auto popup.')

    form_assist_intent_bubble_timer = models.IntegerField(
        default=10, help_text='Form assist intent bubble timer.')

    form_assist_intent_bubble_inactivity_timer = models.IntegerField(
        default=5, help_text='User Inactivity timer during form assist intent bubble.')

    form_assist_intent_bubble_type = models.CharField(
        default="1", help_text='Designates form assist intent bubble type for the bot.', max_length=20)

    form_assist_auto_pop_text = models.TextField(default="Welcome. How may I help you today?",
                                                 null=True, blank=True, help_text='This text will be visible instead of bot pop up')

    form_assist_intent_bubble = models.ManyToManyField(
        'Intent', blank=True, help_text="Intents for this form assist intent bubble.")

    is_voice_based_form_assist_enabled = models.BooleanField(
        default=False, help_text="Designates whether voice based form assist is enabled or not.")

    enable_response_form_assist = models.BooleanField(
        default=True, help_text="Enabling this will allow the users to respond on the fields that are mapped.")

    class Meta:
        verbose_name = "FormAssistBotData"
        verbose_name_plural = "FormAssistBotData"

    def __str__(self):
        return str(self.bot.name)


class Bot(models.Model):

    name = models.CharField(max_length=100, help_text="Bot name")

    slug = models.SlugField(null=True, blank=True, help_text="Bot Slug")

    bot_display_name = models.CharField(
        max_length=100, null=True, blank=True, help_text="Bot display name.")

    trigger_keywords = models.TextField(blank=True, null=True)

    stop_keywords = models.TextField(blank=True, null=True)

    font = models.TextField(default="Roboto", null=True, help_text="Bot Font")

    font_size = models.TextField(
        default="14px", null=True, help_text="Bot Font Size")

    BOT_TYPE = (
        ('Composite', 'Composite'),
        ('Simple', 'Simple'),
    )

    bot_type = models.CharField(
        max_length=10,
        choices=BOT_TYPE,
        default='Simple',
        help_text="Type of bot."
    )

    child_bots = models.ManyToManyField(
        'Bot', blank=True, help_text="Specific child bots for this bot.")

    users = models.ManyToManyField(
        User, blank=True, help_text="Specific users who can access the bot.")

    bot_theme_color = models.CharField(
        max_length=100, default='0F52A1', help_text="Bot theme color code.")

    is_enable_gradient = models.BooleanField(
        default=True, help_text="If this is enabled then linear gradient will be applied on chatbot navbar.")

    bot_image = models.ImageField(
        upload_to=settings.IMAGE_UPLOAD_PATH, null=True, blank=True, help_text="Bot image", max_length=1000)

    bot_logo = models.ImageField(
        upload_to=settings.IMAGE_UPLOAD_PATH, null=True, blank=True, help_text="Bot logo", max_length=1000)

    message_image = models.ImageField(
        upload_to=settings.IMAGE_UPLOAD_PATH, null=True, blank=True, help_text="Bot welcome message image", max_length=1000)

    languages_supported = models.ManyToManyField(
        'Language', blank=True, help_text="Specific languages supported by bot.")

    is_uat = models.BooleanField(
        default=True, help_text="Designates whether bot is uat for not.")

    is_active = models.BooleanField(
        default=False, help_text="Designates whether bot is currently active or not.")

    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether bot is deleted or not. Select this instead of deleting the bot.")

    is_text_to_speech_required = models.BooleanField(
        default=False, help_text="Designates whether text to speech is required or not.")

    is_easy_search_allowed = models.BooleanField(
        default=False, help_text="Designates whether EasySearch is allowed in the bot or not.")

    terms_and_condition = models.TextField(
        null=True, blank=True, help_text="Terms and Conditions")

    is_form_assist_enabled = models.BooleanField(
        default=False, help_text="Designates whether form assist is enabled or not.")

    is_livechat_enabled = models.BooleanField(
        default=False, help_text="Designates whether live chat is enabled or not.")

    is_image_upload_allowed_in_livechat = models.BooleanField(
        default=True, help_text="Designates whether image upload is allowed in livechat.")

    is_easy_assist_allowed = models.BooleanField(
        default=False, help_text='Designates whether cobrowsing is enabled or not')

    is_pdf_search_allowed = models.BooleanField(
        default=False, help_text='Designates whether pdf search is enabled or not'
    )

    is_tms_allowed = models.BooleanField(
        default=False, help_text='Designates whether TMS is enabled or not')

    is_whatsapp_tms_allowed = models.BooleanField(
        default=False, help_text='Designates whether TMS is enabled or not For whatsapp channel')

    livechat_default_intent = models.ForeignKey(
        'Intent', null=True, blank=True, on_delete=models.SET_NULL, help_text="Default intent for live chat.")

    is_lead_generation_enabled = models.BooleanField(
        default=False, help_text="Designates whether the bot is lead generation bot or not.")

    start_conversation = models.CharField(
        max_length=200, null=True, blank=True)

    intent_score_threshold = models.FloatField(
        default=0.0, help_text="Threshold value for intent matching score.")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when bot is created.")

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="creator", help_text="User, who has created this bot.")

    max_suggestions = models.IntegerField(
        default=6, help_text="This number of suggestions should be shown.")

    is_auto_pop_allowed = models.BooleanField(
        default=False, help_text="Designates whether bot auto popup is allowed or not.(This field is not used)")

    is_auto_pop_allowed_desktop = models.BooleanField(
        default=True, help_text="Designates whether bot auto popup is allowed or not for desktop.")

    is_auto_pop_allowed_mobile = models.BooleanField(
        default=True, help_text="Designates whether bot auto popup is allowed or not for mobile.")

    auto_popup_type = models.CharField(
        default="2", help_text='Designates auto popup type for the bot.', max_length=20)

    auto_pop_timer = models.IntegerField(
        default=5, help_text='Bot will automatically pop after this many seconds')

    auto_pop_text = models.TextField(default="Welcome. How may I help you today?",
                                     null=True, blank=True, help_text='This text will be visible instead of bot pop up')

    is_auto_popup_inactivity_enabled = models.BooleanField(
        default=True, help_text="Designates whether bot should auto popup only while the user is inactive or not.")

    default_theme = models.ForeignKey(
        'EasyChatTheme', null=True, blank=True, on_delete=models.SET_NULL, help_text="Default bot theme.")

    bot_position = models.CharField(
        choices=BOT_POSITION_CHOICES, max_length=20, default="bottom-right", help_text="Position of bot on the website.")

    bot_image_visible = models.BooleanField(
        default=True, help_text="Designates whether bot image is visible or not.")

    is_powered_by_required = models.BooleanField(
        default=False, help_text="Designates whether powered by CognoAI should b show on bot or not.")

    is_feedback_required = models.BooleanField(
        default=False, help_text='Designates whether allow intent feedback at intent level')

    show_intent_threshold_functionality = models.BooleanField(
        default=False, help_text='Designates whether threshold can be changed from client side or not')

    is_form_assist_auto_pop_allowed = models.BooleanField(
        default=False, help_text="Designates whether form asssit auto popup is allowed or not.")

    form_assist_autopop_up_timer = models.IntegerField(
        default=10, help_text='Form assist autobot popup timer.')

    form_assist_inactivity_timer = models.IntegerField(
        default=20, help_text='User Inactivity timer during form assist.')

    go_live_date = models.DateTimeField(
        default=timezone.now, help_text="Go Live date for bot")

    flow_termination_keywords = models.TextField(
        default='{"items":["stop","exit"]}', help_text="Flow termination keywords")

    flow_termination_bot_response = models.TextField(
        default='Hi, this is your virtual assistant. Please type "Hi" to start chatting with me.', blank=True, help_text="Flow termination bot response")

    flow_termination_confirmation_display_message = models.TextField(
        default="You were already in the middle of a conversation, would you like me to abort it?", blank=True, help_text="Flow termination confirmation display message")

    is_nps_required = models.BooleanField(
        default=False, help_text='Designates whether allow feedback at bot level')

    is_small_talk_disable = models.BooleanField(
        default=False, help_text="Designates whether all small intents are disabled in this bot or not.")

    is_synonyms_included_in_paraphrase = models.BooleanField(
        default=False, help_text="Designates whether sysnonyms are included in paraphrase generation or not.")

    is_email_notifiication_enabled = models.BooleanField(
        default=False, help_text="Is email notifications enabled on this bot")

    mask_confidential_info = models.BooleanField(
        default=True, help_text="Designates whether masking of confidential data is permitted or not.")

    is_api_fail_email_notifiication_enabled = models.BooleanField(
        default=False, help_text="Is email notifications on API failed enabled on this bot")

    mail_sender_time_interval = models.IntegerField(
        null=True, blank=True, help_text='The time interval between two mail sent for same API failure in minutes.')

    mail_sent_to_list = models.TextField(
        default="{\"items\":[]}", blank=True, help_text='The list of user to whom the mail needs to be sent.')

    is_inactivity_timer_enabled = models.BooleanField(
        default=False, help_text="Designates whether Inactivity timer enabled for bot or not")

    bot_inactivity_timer = models.IntegerField(
        default=15, help_text='User Inactivity timer during Bot Interaction')

    is_analytics_monitoring_enabled = models.BooleanField(
        default=False, help_text="Designates whether Analytics Monitoring enabled for bot or not")

    bot_inactivity_response = models.TextField(
        default="I'm still here. Please let me know if you have any queries.", help_text='Bot response when Inactivity detected Bot Interaction')

    static_analytics = models.BooleanField(
        default=False, help_text='show static analytics for demo')

    bot_userid_cookie_timeout = models.IntegerField(
        default=0, help_text='in minutes. User Id cookie will be expired after x minute of inactivity.')

    initial_intent = models.ForeignKey(
        'Intent', null=True, blank=True, on_delete=models.SET_NULL, related_name='+', help_text="Initial intent trigger.")

    is_minimization_enabled = models.BooleanField(
        default=False, help_text='allow user to minimized the bot icon when deployed on webpage')

    disable_auto_popup_minimized = models.BooleanField(
        default=False, help_text='allow user to disable auto popup when bot is in minimized state')

    invocation = models.TextField(null=True, blank=True)

    show_brand_name = models.BooleanField(
        default=True, help_text="Show company's brand name if set to true")

    is_custom_js_required = models.BooleanField(
        default=False, help_text="Designated whether bot is using custom js or not.")

    is_custom_css_required = models.BooleanField(
        default=False, help_text="Designated whether bot is using custom css or not.")

    bot_response_delay_allowed = models.BooleanField(
        default=True, help_text="Designated whether delay message is allowed or not.")

    bot_response_delay_timer = models.IntegerField(
        default=10, help_text='Deplay message will be seen after this much of time.')

    bot_response_delay_message = models.TextField(
        default="Hang on for a second, I'm processing the details you just shared", help_text='Bot response when response is deplayed.')

    web_url_landing_data = models.TextField(
        default=[], help_text="Web URL based landing data.")

    auto_popup_initial_messages = models.TextField(
        default="[]", help_text="List of initial intents to trigger.")

    web_url_initial_intent_present = models.BooleanField(
        default=False, help_text="Is Initial intent present")
    web_url_is_welcome_message_present = models.BooleanField(
        default=False, help_text="Is welcome message present")
    web_url_initial_image_present = models.BooleanField(
        default=False, help_text="Is initial image present")
    web_url_initial_videos_present = models.BooleanField(
        default=False, help_text="Is initial video present")
    web_url_is_welcome_banner_present = models.BooleanField(
        default=False, help_text="Is welcome banner present")

    default_order_of_response = models.TextField(
        default="[]", help_text="Default order of response for all intents.")
    max_file_size_allowed = models.IntegerField(
        default=5, help_text="max file size allowed for file attachment")

    suggestion_list = models.TextField(
        default="[]", help_text="Suggestion list of all intents.")
    word_mapper_list = models.TextField(
        default="[]", help_text="Word mapper list of all word mappers added.")
    last_query_time = models.DateTimeField(
        default=timezone.now, help_text="Last time, when any of bot's user has asked query. It helps to update word_mapper_list and suggestion_list")
    show_livechat_form_or_no = models.BooleanField(
        default=True, blank=False, null=False)
    use_show_customer_detail_livechat_processor = models.BooleanField(
        default=False, blank=False, null=False)
    use_end_chat_processor_livechat = models.BooleanField(
        default=False, blank=False, null=False)
    use_assign_agent_processor_livechat = models.BooleanField(
        default=False, blank=False, null=False)
    number_of_words_in_user_message = models.IntegerField(
        default=200, help_text='User messages will be restricted to a certain number of characters.')

    number_of_nlp_suggestion_allowed = models.IntegerField(
        default=5, help_text='Number of suggestion allowed in Did you mean?')

    autcorrect_replace_bot = models.CharField(max_length=50, blank=True, default="\-\+,#!<>/\";'^`",
                                              help_text='Characters in this text field will be kept as it is. Characters in this list will be replaced by blank.')

    last_bot_updated_datetime = models.DateTimeField(default=timezone.now)

    masking_enabled = models.BooleanField(
        default=True, help_text="Designates whether masking pii data is enabled or not")

    masking_time = models.IntegerField(
        default=20, help_text='Time (in min) after which data will be masked')

    csat_feedback_form_enabled = models.BooleanField(
        default=False, blank=False, null=False)

    scale_rating_5 = models.BooleanField(
        default=False, blank=False, null=False, help_text="Whether Csat rating scale is 5 or 4")

    max_feedback_allowed = models.IntegerField(
        default=5, blank=False, null=False)

    enable_audio_notification = models.BooleanField(
        default=True, help_text="Designates whether audio notification to be given to customer on new message when bot is minimized")

    need_to_build = models.BooleanField(
        default=False, help_text="Designates whether this bot is required to be build again or not")

    enable_intent_level_nlp = models.BooleanField(
        default=False, help_text="Designates whether intent level nlp settings are enabled.")

    is_easychat_ner_required = models.BooleanField(
        default=True, help_text="Is name entity relationship and parts of speech recogniztion required")

    class Meta:
        verbose_name = "Bot"
        verbose_name_plural = "Bots"

    def __str__(self):
        return self.name + " - " + str(self.bot_type) + " - " + str(self.is_uat)

    def get_score(self, stem_words):
        try:
            trigger_keywords = json.loads(self.trigger_keywords)

            stop_keywords = json.loads(self.stop_keywords)

            trigger_keywords_list = [keyword_dict[
                'tag'] for keyword_dict in trigger_keywords if keyword_dict['tag'] != ""]

            stop_keywords_list = [keyword_dict[
                'tag'] for keyword_dict in stop_keywords if keyword_dict['tag'] != ""]

            trigger_keywords_str = " ".join(trigger_keywords_list)

            stop_keywords_str = " ".join(stop_keywords_list)

            trigger_stem_keywords = get_stem_words_of_sentence(
                trigger_keywords_str, None, None, None, None)

            stop_stem_keywords = get_stem_words_of_sentence(
                stop_keywords_str, None, None, None, None)

            if len(list(set(stop_stem_keywords) & set(stem_words))) > 0:
                return [0, 0]

            positive_score = len(
                list(set(trigger_stem_keywords) & set(stem_words)))

            negative_score = positive_score - len(trigger_stem_keywords)

            return [positive_score, negative_score]
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP] %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return [0, 0]

    def remove_all_child_bots(self):
        self.child_bots.clear()

    def is_accessible(self, user_obj):
        access_manage_objs = AccessManagement.objects.filter(
            bot=self, user=user_obj)
        access_type_names = []
        if len(access_manage_objs) > 0:
            access_type_names = access_manage_objs[
                0].access_type.all().values_list('name', flat=True)
        return list(access_type_names)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.pk == None or self.bot_display_name == None or self.bot_display_name == "":
            self.bot_display_name = self.name
        if self.bot_image.name is not None and len(self.bot_image.name) > 1000:
            raise ValueError(
                "Bot image path length is greater then Max length - ", 1000)
        if self.message_image.name is not None and len(self.message_image.name) > 1000:
            raise ValueError(
                "Bot message image path length is greater then Max length - ", 1000)
        if self.name is not None and len(self.name) > self._meta.get_field('name').max_length:
            raise ValueError("Bot name length is greater then Max length - ",
                             self._meta.get_field('name').max_length)
        super(Bot, self).save(*args, **kwargs)

    def disable(self):  # noqa F811
        self.is_deleted = True
        self.save()

    def get_invocation_name_lower_list(self):
        default_invocation = "talk to " + self.name.lower().strip()
        if self.invocation == None:
            return [default_invocation]
        else:
            return [invocation_sentence.lower() for invocation_sentence in self.invocation.lower().split(',') if invocation_sentence != ""] + [default_invocation]

    def get_bot_theme_light_color(self):
        try:
            theme_color = (self.bot_theme_color)
            red = str(int(theme_color[0:2], 16))
            green = str(int(theme_color[2:4], 16))
            blue = str(int(theme_color[4:6], 16))
            # converting the hex color into rgb color and giving opacity 0.04
            # for making it lighter
            return "rgba(" + red + "," + green + "," + blue + ",0.04)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_bot_theme_light_color no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
            pass

        return "rgb(226, 239, 255)"

    def get_bot_theme_light_color_two(self):
        try:
            theme_color = (self.bot_theme_color)
            red = str(int(theme_color[0:2], 16))
            green = str(int(theme_color[2:4], 16))
            blue = str(int(theme_color[4:6], 16))
            # converting the hex color into rgb color and giving opacity 0.8
            # for making it lighter
            return "rgba(" + red + "," + green + "," + blue + ",0.7)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_bot_theme_light_color_two no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
            pass

        return "rgb(226, 239, 255)"

    def get_feedback_slider_colour(self):
        try:
            feedback_slider_colour = "linear-gradient(90deg, " + self.get_bot_theme_light_color(
            ) + " 0%, #" + self.bot_theme_color + " 98.29%)"
            return feedback_slider_colour
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("some problem in feedback slider colour no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
            pass
        return "rgb(226, 239, 255)"


@receiver(post_save, sender=Bot)
def add_static_category(sender, instance, **kwargs):
    category_list = ["Credit Card", "Home Loan", "Savings Account"]
    if instance.static_analytics:
        for category in category_list:
            try:
                Category.objects.get(bot=instance, name=category)
            except Exception:
                Category.objects.create(bot=instance, name=category)


@receiver(post_save, sender=Bot)
def create_bot_channel(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        channels = Channel.objects.filter(is_easychat_channel=True)
        activity_update = {
            "is_welcome_message_updated": "false",
            "is_failure_message_updated": "false",
            "is_authentication_message_updated": "false",
            "is_auto_pop_up_text_updated": "false",
            "is_web_prompt_message_updated": "[]",
        }
        activity_update = json.dumps(activity_update)
        for channel in channels:
            if BotChannel.objects.filter(bot=instance, channel=channel).count() == 0:
                BotChannel.objects.create(
                    bot=instance, channel=channel, activity_update=activity_update)

        try:
            bot_channel_obj = BotChannel.objects.get(
                bot=instance, channel=channels.filter(name="Voice").first())
            if not VoiceBotConfiguration.objects.filter(bot_channel=bot_channel_obj):
                VoiceBotConfiguration.objects.create(
                    bot_channel=bot_channel_obj)
        except Exception as e:
            logger.error(str(e), extra={'AppName': 'EasyChat', 'user_id': 'None',
                         'source': 'None', 'channel': 'None', 'bot_id': 'None'})


@receiver(post_save, sender=Bot)
def create_ticket_category(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        TicketCategory.objects.create(bot=instance,
                                      ticket_category="Others",
                                      ticket_period=3)


@receiver(post_save, sender=Bot)
def create_intent_category(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        Category.objects.create(bot=instance, name="Others")


@receiver(post_save, sender=Bot)
def create_bot_info(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        import os
        activity_update = {
            "is_bot_inactivity_response_updated": "false",
            "is_bot_response_delay_message_updated": "false",
            "is_flow_termination_bot_response_updated": "false",
            "is_flow_termination_confirmation_display_message_updated": "false",
        }
        activity_update = json.dumps(activity_update)
        if BotInfo.objects.filter(bot=instance).count() == 0:
            words_file = os.path.join(
                (os.path.abspath(os.path.dirname(__file__))), 'badwords.txt')
            with open(words_file, 'r') as f:
                censor_list = [line.strip() for line in f.readlines()]
            bad_words = json.dumps(censor_list)
            BotInfo.objects.create(
                bot=instance, activity_update=activity_update, bad_keywords=bad_words)


@receiver(post_save, sender=Bot)
def create_emoji_bot_response(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        if EmojiBotResponse.objects.filter(bot=instance).count() == 0:
            EmojiBotResponse.objects.create(bot=instance)


@receiver(post_save, sender=Bot)
def create_profanity_bot_response(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        if ProfanityBotResponse.objects.filter(bot=instance).count() == 0:
            ProfanityBotResponse.objects.create(bot=instance)


@receiver(post_save, sender=Bot)
def set_bot_object_cache(sender, instance, **kwargs):
    cache.set("BotObject-" + str(instance.pk), instance, settings.CACHE_TIME)


class LanguageTunedBot(models.Model):
    language = models.ForeignKey(
        'Language', blank=True, null=True, on_delete=models.CASCADE, help_text="Language obj which is to be tuned")

    bot = models.ForeignKey(
        'Bot', blank=True, null=True, on_delete=models.CASCADE, help_text="Bot obj of the coresponding language")

    auto_pop_up_text = models.TextField(default="",
                                        null=True, blank=True, help_text='This text will be language tuned in autopopup text')

    flow_termination_keywords = models.TextField(
        default="{\"items\":[]}", help_text="Flow termination keywords")

    flow_termination_bot_response = models.TextField(
        default="", blank=True, help_text="Flow termination bot response")

    bot_response_delay_message = models.TextField(
        default="", help_text='Bot response when response is deplayed.')

    bot_inactivity_response = models.TextField(
        default="", help_text='Bot response when Inactivity detected Bot Interaction')

    flow_termination_confirmation_display_message = models.TextField(
        default="", blank=True, help_text="Flow termination confirmation display message")

    terms_and_condition = models.TextField(default="",
                                           null=True, blank=True, help_text="Terms and Conditions")

    web_url_landing_data = models.TextField(
        default=[], help_text="Web URL based landing data.")

    form_assist_popup_text = models.TextField(default="",
                                              null=True, blank=True, help_text='This text will be language tuned in form assist autopopup text')

    emoji_angry_response_text = models.TextField(
        default="", blank=True, help_text="Angry Emoji Response")

    emoji_happy_response_text = models.TextField(
        default="", blank=True, help_text="Happy Emoji Response")

    emoji_neutral_response_text = models.TextField(
        default="", blank=True, help_text="Neutral Emoji Response")

    emoji_sad_response_text = models.TextField(
        default="", blank=True, help_text="Sad Emoji Response")

    profanity_bot_response = models.TextField(
        default="", blank=True, help_text="Profanity Bot Response")

    whatsapp_catalogue_data = models.TextField(
        default={}, blank=True, help_text="WhatsApp Catalogue Data")

    class Meta:
        verbose_name = "LanguageTunedBot"
        verbose_name_plural = "LanguageTunedBots"

    def __str__(self):
        return str(self.bot.name) + " - " + self.language.name_in_english


class LanguageTunedBotChannel(models.Model):

    language = models.ForeignKey(
        'Language', blank=True, null=True, on_delete=models.CASCADE, help_text="Language obj which is to be tuned")

    bot_channel = models.ForeignKey(
        'BotChannel', blank=True, null=True, on_delete=models.CASCADE, help_text="Bot Channel obj of the coresponding language")

    welcome_message = models.CharField(
        default="Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?", max_length=500, help_text="Bot welcome text message.")

    failure_message = models.CharField(
        default="I'm not sure if I can help you with your query. Can you please rephrase it? Alternatively, you can connect to our customer care team, who is always there to help you!", max_length=500, help_text="Failure message shown when bot is unable to give answer.")

    authentication_message = models.CharField(
        default="Please complete authentication to use this service", max_length=500, help_text="Message shown when authentication is required.")

    block_spam_data = models.TextField(
        default={}, blank=True, help_text="Block Spam Data")

    class Meta:
        verbose_name = "LanguageTunedBotChannel"
        verbose_name_plural = "LanguageTunedBotChannels"

    def __str__(self):
        return str(self.bot_channel) + " - " + self.language.name_in_english


class BotChannel(models.Model):

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE, help_text="Bot channel")

    languages_supported = models.ManyToManyField(
        'Language', blank=True, help_text="Specific languages supported by this Bot Channel")

    welcome_message = models.CharField(
        default="Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?", max_length=500, help_text="Bot welcome text message.")

    speech_message = models.CharField(
        default="Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?", max_length=500, help_text="Bot welcome speech message.")

    failure_message = models.CharField(
        default="I'm not sure if I can help you with your query. Can you please rephrase it? Alternatively, you can connect to our customer care team, who is always there to help you!", max_length=500, help_text="Failure message shown when bot is unable to give answer.")

    authentication_message = models.CharField(
        default="Please complete authentication to use this service", max_length=500, help_text="Message shown when authentication is required.")

    reprompt_message = models.CharField(
        default="Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?", max_length=500, help_text="Reprompt message.")

    session_end_message = models.CharField(
        default="Thanks you for using EasyChat.", max_length=500, help_text="Message shown when session is ended")

    initial_messages = models.TextField(
        default="{\"items\":[]}", help_text="Initial messages.")

    sticky_intent = models.TextField(
        default="{\"items\":[]}", help_text="Sticky Intents.")

    channel_params = models.TextField(
        default="{}", null=True, blank=True, help_text="Channel params")

    image_url = models.TextField(
        default="{\"items\":[]}", null=True, blank=True, help_text="Image url.")

    redirection_url = models.TextField(
        default="{\"items\":[]}", null=True, blank=True, help_text="Redirection url")

    failure_recommendations = models.TextField(
        default="{\"items\":[]}", help_text="Failure messages.")

    verification_code = models.CharField(
        null=True, blank=True, max_length=500, help_text="Facebook Verification Token")

    page_access_token = models.CharField(
        null=True, blank=True, max_length=500, help_text="Facebook Page Access Token")

    is_email_notifiication_enabled = models.BooleanField(
        default=False, help_text="Is email notifications on endpoint failure from vendor side enabled for this bot channel.")

    mail_sender_time_interval = models.IntegerField(
        null=True, blank=True, help_text='The time interval between two mail sent for same endpoint failure(minutes).')

    mail_sent_to_list = models.TextField(
        default="{\"items\":[]}", blank=True, help_text='The list of user to whom the mail needs to be sent.')

    is_automatic_carousel_enabled = models.BooleanField(
        default=False, help_text="Is carousel in the bot is enabled for automatic movement")

    carousel_time = models.IntegerField(
        default=5, help_text='The time interval between movement of images in the bot carousel')

    ms_team_app_code = models.CharField(
        null=True, blank=True, max_length=1024, help_text="MS Teams App Code")

    ms_team_app_password = models.CharField(
        null=True, blank=True, max_length=1024, help_text="MS Teams App Password")

    integrated_whatsapp_mobile = models.CharField(
        null=True, blank=True, max_length=10, help_text='This bot is integrated with WhatsApp on this mobile number.')

    is_bot_notification_sound_enabled = models.BooleanField(
        default=True, help_text="Is bot message notification sound enabled for this bot channel.")

    sticky_button_display_format = models.CharField(
        max_length=256, default="Button", choices=STICKY_BUTTON_DISPLAY_CHOICES, help_text="Select display format for sticky buttons ")

    sticky_intent_menu = models.TextField(
        default="{\"items\":[]}", help_text="Sticky Intents in menu format.")

    hamburger_items = models.TextField(
        default="{\"items\":[]}", help_text="Hamburger Items.")

    quick_items = models.TextField(
        default="{\"items\":[]}", help_text="Quick Menu Items.")

    mobile_number_masking_enabled = models.BooleanField(
        default=False, help_text="Designates whether mobile number masking is allowed or not in whatsapp channel")

    activity_update = models.TextField(
        default="{}", help_text="Stores information wheter a particular field is edited or not")

    is_web_bot_phonetic_typing_enabled = models.BooleanField(
        default=False, help_text="Is phonetic typing enabled for this bot in web channel")

    phonetic_typing_disclaimer_text = models.CharField(null=True, blank=True,
                                                       default="This will translate conversations across the bot into [Language selected] and translations might not be accurate everywhere. Do you still want to continue?", max_length=256, help_text="disclaimer text to be shown.")

    api_key = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text='key to access api')

    is_language_auto_detection_enabled = models.BooleanField(
        default=False, help_text="Is Auto detection of language enabled for this particular channel")

    is_enable_choose_language_flow_enabled_for_welcome_response = models.BooleanField(
        default=False, help_text="this is to show change language option when user comes for the first time in channels other than web")

    is_nlp_suggestions_required = models.BooleanField(
        default=True, help_text="If this is true then NLP suggestions will be shown")

    voice_modulation = models.TextField(default=json.dumps(
        DEFAULT_VOICE_MODULATION), null=True, blank=True)

    is_textfield_input_enabled = models.BooleanField(
        default=True, help_text="Designates whether the user will be shown the input text field in bot or not.")

    return_initial_query_response = models.BooleanField(default=False, help_text="If this toggle is enabled then initial query response will be returned else welcome response will be shown.")

    class Meta:
        verbose_name = "BotChannel"
        verbose_name_plural = "BotChannel"

    def __str__(self):
        return self.bot.name + " - " + self.channel.name

    def get_mail_sent_to_list(self):
        try:
            return json.loads(self.mail_sent_to_list)["items"]
        except Exception:
            return []


class BuiltInIntentIcon(models.Model):

    unique_id = models.IntegerField(help_text="Unique Id of intent icon")

    icon = models.TextField(null=True, blank=True,
                            help_text="SVG code of icon")

    def __str__(self):
        return str(self.unique_id)

    class Meta:
        verbose_name = "BuiltInIntentIcon"
        verbose_name_plural = "BuiltInIntentIcons"


class Intent(models.Model):

    name = models.CharField(max_length=5000, help_text="Intent name")

    intent_hash = models.CharField(max_length=5000, default="", db_index=True, blank=True,
                                   null=True, help_text="Hashed value of intent name ater removing stop words")

    multilingual_name = models.CharField(
        max_length=5000, blank=True, help_text="Multilingual name")

    bots = models.ManyToManyField(
        'Bot', blank=True, help_text="Specific bots where this intent can be used.")

    tree = models.ForeignKey(
        'Tree', null=True, blank=True, on_delete=models.CASCADE, help_text="Tree of the intent.")

    keywords = models.TextField(
        default="{}", null=True, blank=True, help_text="Keywords for the intent.")

    training_data = models.TextField(
        default="{}", null=True, blank=True, verbose_name="Training Data", help_text="Training data for the intent.")

    restricted_keywords = models.TextField(
        default="", null=True, blank=True, help_text="Restricted keywords.")

    necessary_keywords = models.TextField(
        default="", null=True, blank=True, help_text="Necessary keywords.")

    common_keywords = models.TextField(
        default="", null=True, blank=True, help_text="Common keywords")

    training_data_with_pos = models.TextField(
        default="{}", null=True, blank=True, verbose_name="Training Data With Parts of Speech", help_text="Training data for the intent.")

    channels = models.ManyToManyField(
        'Channel', blank=True, help_text="Specific channels where this intent can be used.")

    threshold = models.FloatField(
        default=1.0, help_text="Threshold value of the intent.")

    last_modified = models.DateField(
        default=now, help_text="Last intent modified date.")

    is_feedback_required = models.BooleanField(
        default=True, help_text="Designates whether feedback is required or not.")

    # is_attachment_required = models.BooleanField(default=False)

    # choosen_file_type = models.TextField(default="", null=True, blank=True)

    is_authentication_required = models.BooleanField(
        default=False, help_text="Designates whether authentication is required for this intent or not.")

    is_part_of_suggestion_list = models.BooleanField(
        default=True, help_text="Designates whether intent should be a part of suggestion list or not.")

    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether intent is deleted or not. Select this instead of deleting the intent.")

    is_livechat_enabled = models.BooleanField(
        default=False, help_text="Designates whether live chat intent or not.")

    is_form_assist_enabled = models.BooleanField(
        default=False, help_text="Designates whether this is a form assist intent or not.")

    is_hidden = models.BooleanField(
        default=False, help_text="Designates whether this intent is hidden or not.")

    is_small_talk = models.BooleanField(
        default=False, help_text="Designates whether this intent is a small talk intent or not.")

    auth_type = models.ForeignKey(
        'Authentication', on_delete=models.SET_NULL, null=True, blank=True, help_text="Auth Type")

    category = models.ForeignKey(
        'Category', blank=True, null=True, on_delete=models.SET_NULL, help_text="Category")

    is_easy_assist_allowed = models.BooleanField(default=False)

    is_easy_tms_allowed = models.BooleanField(default=False)

    is_whatsapp_csat = models.BooleanField(default=False)

    intent_click_count = models.IntegerField(default=0)

    campaign_link = models.CharField(max_length=2048, null=True, blank=True)

    is_category_response_allowed = models.BooleanField(
        default=False, help_text="Designates whether category based intent response is allowed or not.")

    is_custom_order_selected = models.BooleanField(
        default=False, help_text="Designates whether custom order is selected for order of response")

    order_of_response = models.TextField(
        default="[]", help_text="Order of response for the intent.")

    is_part_of_initial_web_trigger_intent = models.BooleanField(
        default=False, help_text="Designates whether it's part of initial web trigger intents.")

    synced = models.BooleanField(
        default=False, help_text="Designates whether it is synced with word mapper or not.")

    trained = models.BooleanField(
        default=False, help_text="Designates whether this intent is trained or not.")

    build_in_intent_icon = models.ForeignKey(BuiltInIntentIcon, null=True, blank=True, default=get_default_intent_icon, on_delete=models.SET_DEFAULT,
                                             help_text="If built-in intent is selected then this field will have selected built-in intent icon object.")

    intent_icon = models.TextField(
        null=True, blank=True, help_text="If user has uploaded any intent icon then the path of the same will be saved in this field.")

    is_faq_intent = models.BooleanField(
        default=False, help_text="Designates whether the intent is FAQ Intent (Only for theme 4)")

    class Meta:
        verbose_name = "Intent"
        verbose_name_plural = "Intents"

    def disable(self):  # noqa F811
        self.is_deleted = True
        self.save()

    def get_score(self, stem_words, src, channel, user_id, user_query, bot_obj, user_query_stem_words_with_pos_list):
        try:
            keyword_dict = json.loads(self.keywords)

            training_dict = json.loads(self.training_data)

            training_data_with_pos = json.loads(self.training_data_with_pos)

            restricted_keyword_list = self.restricted_keywords.split(",")

            necessary_keyword_list = self.necessary_keywords.split(",")

            common_keywords_list = self.common_keywords.split(",")

            stemmed_restricted_keyword_list = [word_stemmer(
                keyword) for keyword in restricted_keyword_list if keyword != ""]

            stemmed_necessary_keyword_list = [word_stemmer(
                keyword) for keyword in necessary_keyword_list if keyword != ""]

            stemmed_common_keywords_list = [
                keyword for keyword in common_keywords_list if keyword != ""]

            final_score_list = []

            len_necessary_keyword_list = len(stemmed_necessary_keyword_list)

            len_common_keywords_list = len(stemmed_common_keywords_list)

            consider_for_scoring = True

            if len(list(set(stemmed_restricted_keyword_list) & set(stem_words))) > 0:
                logger.info("[NLP]: restricted keyword found", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
                consider_for_scoring = False

            if len(list(set(stemmed_necessary_keyword_list) & set(stem_words))) != len_necessary_keyword_list:
                logger.info("[NLP]: necessary keyword not found", extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
                consider_for_scoring = False

            if len_common_keywords_list > 0 and len(list(set(stemmed_common_keywords_list) & set(stem_words))) != len_common_keywords_list:
                logger.info("[NLP]: common keyword not found : %s", self.pk, extra={'AppName': 'EasyChat', 'user_id': str(
                    user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
                consider_for_scoring = False

            total_stopwords = stopwords.words("english")

            for index_key in keyword_dict.keys():
                score = 0
                stem_keyword_list = list(keyword_dict[index_key].split(","))
                if bot_obj.is_easychat_ner_required and index_key in training_data_with_pos and len(user_query_stem_words_with_pos_list):
                    training_ques_with_pos = list(
                        training_data_with_pos[index_key].split(","))
                    common_tokens = list(
                        set(user_query_stem_words_with_pos_list).intersection(set(training_ques_with_pos)))
                    score = len(common_tokens)
                    query_token_not_matched = score - len(user_query_stem_words_with_pos_list)
                else:
                    common_tokens = list(
                        set(stem_words).intersection(set(stem_keyword_list)))
                    score = len(common_tokens)
                    query_token_not_matched = score - len(stem_words)
                stopwords_tokens = list(
                    set(stem_words).intersection(set(total_stopwords)))
                total_stopwords_score = len(stopwords_tokens)
                tokens_matched = score
                tokens_not_matched = score - len(stem_keyword_list)
                training_question = training_dict[index_key]
                final_score_list.append(
                    [tokens_matched, tokens_not_matched, consider_for_scoring, total_stopwords_score, query_token_not_matched, training_question, len(stem_keyword_list)])

            if final_score_list == []:
                return [0, 0, consider_for_scoring, 0, 0]

            final_score_list = sorted(
                final_score_list, key=lambda element: (element[0], element[1], element[4]))
            final_score_list.reverse()
            return final_score_list[0]

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_obj.pk)})
            return [0, 0, False, 0, 0]

    def save(self, *args, **kwargs):
        try:
            bot_obj = self.bots.all()[0]
            stopwords = ast.literal_eval(bot_obj.stop_keywords)
            if stopwords == "" or stopwords == None:
                stopwords = stop
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Error during saving intent is %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
            stopwords = stop

        keyword_dict = {}

        training_data = json.loads(self.training_data)

        global_training_common_list = []

        for key in training_data.keys():
            question = training_data[key]
            # Preprocess the string
            question = process_string_for_intent_identification(
                question, None, None, None, None)
            # Word Tokenizer
            token_list = nltk.word_tokenize(question)
            # Remove stop word from token list
            token_list = [
                token for token in token_list if token not in stopwords]
            new_token_list = []
            keyword_set = set()
            for token in token_list:
                if token != "":
                    new_token_list.append(word_stemmer(token))
                    keyword_set.add(word_stemmer(token))

            global_training_common_list.append(new_token_list)

            keyword_list = list(keyword_set)
            keywords = ','.join(keyword_list)
            keyword_dict[str(key)] = str(keywords)

        common_elements = []

        try:
            common_elements = list(
                reduce(lambda i, j: i & j, (set(x) for x in global_training_common_list)))
        except Exception:
            pass

        self.common_keywords = ",".join(common_elements)

        self.keywords = json.dumps(keyword_dict)
        self.training_data_with_pos = json.dumps(
            get_training_dict_with_pos(training_data, stopwords))
        self.training_data = json.dumps(training_data)

        self.name = remove_whitespace(self.name)
        self.last_modified = now()

        if self.pk == None and self.tree == None:
            tree_obj = Tree.objects.create(name=self.name)
            self.tree = tree_obj

        if self.name is not None and len(self.name) > self._meta.get_field('name').max_length:
            raise ValueError("Intent name length is greater then Max length - ",
                             self._meta.get_field('name').max_length)

        if self.is_authentication_required and self.auth_type == None:
            raise IntentAuthenticationTypeExceptionError(
                "Authentication type can not empty. Intent Name: {}".format(self.name))

        super(Intent, self).save(*args, **kwargs)

    def remove_all_channel_objects(self):
        self.channels.clear()

    def remove_all_bot_objects(self):
        self.bots.clear()

    def remove_initial_intent_on_delete(self):
        try:
            bot_obj = self.bots.all()[0]
            if self.pk == bot_obj.initial_intent.pk:
                self.bots.all().update(initial_intent=None)
        except Exception:
            pass

    def disable(self):  # noqa F811
        self.is_deleted = True
        self.save()

    def get_recommendations(self):
        try:
            if self.tree == None:
                return []

            if self.tree.response == None:
                return []

            recommendations = json.loads(
                self.tree.response.recommendations)["items"]
            logger.info(recommendations, extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            recommendation_list = []
            for recommendation_pk in recommendations:
                recommendation_list.append(
                    Intent.objects.get(pk=int(recommendation_pk)).name)
            logger.info(recommendation_list, extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return recommendation_list
        except Exception:
            return []

    def get_response(self):
        try:
            if self.tree == None:
                return "No response"

            if self.tree.response == None:
                return "No response"

            if self.tree.response.sentence == None:
                return "No response"

            sentences = json.loads(self.tree.response.sentence)["items"]
            text_response = sentences[0]["text_response"]
            # text_response = text_response.replace("<p><br></p>", "<p></p>").replace(
            #     "</p><p>", "<br>").replace("</p>", "").replace("<p>", "")
            text_response = BeautifulSoup(text_response).text.strip()
            text_response = text_response[:200]
            return text_response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_response %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return "No response"

    def get_response_without_html(self):
        try:
            if self.tree == None:
                return "No response"

            if self.tree.response == None:
                return "No response"

            if self.tree.response.sentence == None:
                return "No response"

            sentences = json.loads(self.tree.response.sentence)["items"]
            text_response = sentences[0]["text_response"][:200]
            regex_cleaner = re.compile('<.*?>')
            cleaned_raw_str = re.sub(regex_cleaner, '', text_response)
            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_response %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return "No response"

    def image_exist(self):
        tree_obj = self.tree
        tree_pk_list = get_intent_related_tree_pks_list(tree_obj.pk)

        for tree_pk in tree_pk_list:
            tree_obj = Tree.objects.get(pk=int(tree_pk))

            if tree_obj == None:
                continue

            if tree_obj.response == None:
                continue

            if tree_obj.response.images_exist():
                return True
        return False

    def video_exist(self):
        tree_obj = self.tree
        tree_pk_list = get_intent_related_tree_pks_list(tree_obj.pk)

        for tree_pk in tree_pk_list:
            tree_obj = Tree.objects.get(pk=int(tree_pk))

            if tree_obj == None:
                continue

            if tree_obj.response == None:
                continue

            if tree_obj.response.videos_exist():
                return True
        return False

    def card_exist(self):
        tree_obj = self.tree
        tree_pk_list = get_intent_related_tree_pks_list(tree_obj.pk)

        for tree_pk in tree_pk_list:
            tree_obj = Tree.objects.get(pk=int(tree_pk))

            if tree_obj == None:
                continue

            if tree_obj.response == None:
                continue

            if tree_obj.response.cards_exist():
                return True
        return False

    def recommendation_exist(self):
        tree_obj = self.tree
        tree_pk_list = get_intent_related_tree_pks_list(tree_obj.pk)

        for tree_pk in tree_pk_list:
            tree_obj = Tree.objects.get(pk=int(tree_pk))

            if tree_obj == None:
                continue

            if tree_obj.response == None:
                continue

            if tree_obj.response.recommendations_exist():
                return True
        return False

    def get_no_of_variations(self):
        no_of_variations = 0
        data = json.loads(self.training_data)
        no_of_variations = len(data)
        if no_of_variations > 0:
            return no_of_variations
        return None

    def get_comma_seprated_supported_channel_name(self):
        try:
            channels = self.channels.all()
            channel_str = ""

            for channel in channels:
                channel_str = channel_str + channel.name + ","

            return channel_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_response %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            return "all"

    def __str__(self):
        return self.name


@receiver(post_save, sender=Intent)
def check_whether_duplicate_intent_exist(sender, instance, **kwargs):
    bot_objs = instance.bots.all()
    channel_objs = instance.channels.all()
    if bot_objs:
        intent_objs = Intent.objects.filter(
            bots__in=bot_objs, channels__in=channel_objs, is_deleted=False).distinct()
        bot_obj = instance.bots.all()[0]
        # currently an intent is having only one bot a time so to get stem
        # words we are using stop words of that particular bot only
        stem_words = get_stem_words_of_sentence(
            instance.name, None, None, None, bot_obj)
        stem_words.sort()
        hashed_name = ' '.join(stem_words)
        hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
        intent_objs = intent_objs.filter(intent_hash=hashed_name)
        if intent_objs.count() > 1:
            instance.delete()
            raise DuplicateIntentExceptionError(
                "Matching intent already exists. Intent Name: " + str(instance.name))


@receiver(post_save, sender=Intent)
def create_intent_hash(sender, instance, **kwargs):

    try:
        IntentTreeHash.objects.filter(
            tree=instance.tree).delete()
        bot_objs = instance.bots.all()
        training_objs = json.loads(instance.training_data)
        training_data = []

        for key, value in training_objs.items():
            training_data.append(value.strip())

        for bot_obj in bot_objs:
            for training in training_data:
                stem_words = get_stem_words_of_sentence(
                    training, None, None, None, bot_obj)
                if len(stem_words) < 1:
                    continue
                stem_words.sort()
                stem_words_name = ' '.join(stem_words)
                hashed_name = hashlib.md5(stem_words_name.encode()).hexdigest()
                IntentTreeHash.objects.create(
                    tree=instance.tree, stem_words_name=stem_words_name, hash_value=hashed_name, is_tree=False, training_question=training)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_intent_hash! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


class Choice(models.Model):

    display = models.CharField(
        max_length=100, help_text="This is shown to user.")

    value = models.CharField(
        max_length=100, help_text="This has the same value as display.")

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"

    def __str__(self):
        return self.value


class Explanation(models.Model):
    explanation = models.TextField(default="explanation")

    def __str__(self):
        return self.explanation


class BotResponse(models.Model):

    sentence = models.TextField(
        default="{\"items\":[{\"text_response\":\"\", \"speech_response\":\"\", \"text_reprompt_response\":\"\", \"speech_reprompt_response\":\"\", \"tooltip_text\":\"\"}]}")

    choices = models.ManyToManyField(Choice, blank=True)

    recommendations = models.TextField(default="{\"items\":[]}", null=True)

    cards = models.TextField(default="{\"items\":[]}", null=True, blank=True)

    images = models.TextField(default="{\"items\":[]}", null=True, blank=True)

    videos = models.TextField(default="{\"items\":[]}", null=True, blank=True)

    table = models.TextField(default="{\"items\": \"\"}", null=True, blank=True)

    modes = models.TextField(default="{}")

    modes_param = models.TextField(default="{}")

    is_timed_response_present = models.BooleanField(default=False)

    timer_value = models.CharField(
        max_length=100, default=30, null=True, blank=True)

    auto_response = models.CharField(max_length=100, null=True, blank=True)

    activity_update = models.TextField(
        default="{}", help_text="This stores wheter some changes are made in particular fields or not")

    whatsapp_list_message_header = models.TextField(
        default="Options", help_text="WhatsApp list message header", null=True, blank=True)

    class Meta:
        verbose_name = "BotResponse"
        verbose_name_plural = "BotResponse"

    def save(self, *args, **kwargs):

        modes_json = json.loads(self.modes)
        modes_param_json = json.loads(self.modes_param)

        modes = {
            "is_typable": "true",
            "is_button": "true",
            "is_slidable": "false",
            "is_date": "false",
            "is_dropdown": "false",
            "is_datepicker": "false",
            "auto_trigger_last_intent": "false"
        }

        modes_param = {
            "is_slidable": {
                "max": "",
                "min": "",
                "step": ""
            },
            "datepicker_list": [{"placeholder": "Date"}],
            "last_identified_intent": "",
        }

        if modes_json == {}:
            modes_json = modes

        if modes_param_json == {}:
            modes_param_json = modes_param

        self.modes = json.dumps(modes_json)
        self.modes_param = json.dumps(modes_param_json)

        super(BotResponse, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return json.loads(self.sentence)["items"][0]["text_response"][:50]
        except Exception:  # noqa: F841
            return "render error"

    def clear_response_choices(self):
        self.choices.clear()

    def images_exist(self):
        is_image_exist = False
        try:
            images = json.loads(self.images)["items"]
            if len(images) > 0:
                is_image_exist = True
        except Exception:  # noqa: F841
            pass

        return is_image_exist

    def videos_exist(self):
        is_video_exist = False
        try:
            videos = json.loads(self.videos)["items"]
            if len(videos) > 0:
                is_video_exist = True
        except Exception:  # noqa: F841
            pass

        return is_video_exist

    def cards_exist(self):
        is_card_exist = False
        try:
            cards = json.loads(self.cards)["items"]
            if len(cards) > 0:
                is_card_exist = True
        except Exception:  # noqa: F841
            pass

        return is_card_exist

    def table_exist(self):
        is_table_exist = False
        try:
            table = json.loads(self.table)["items"]
            if len(table) > 0:
                is_table_exist = True
        except Exception:  # noqa: F841
            pass

        return is_table_exist

    def recommendations_exist(self):
        is_recommendation_exist = False
        try:
            recommendations = json.loads(self.recommendations)["items"]
            if len(recommendations) > 0:
                is_recommendation_exist = True
        except Exception:  # noqa: F841
            pass

        return is_recommendation_exist


class Processor(models.Model):

    name = models.CharField(default="FunctionName",
                            max_length=100, help_text="Function name")

    function = models.TextField(
        default="def f(x):\n    return x", null=True, blank=True, help_text="Function code")

    processor_lang = models.CharField(max_length=256,
                                      default="1",
                                      null=True,
                                      blank=True,
                                      choices=LANGUAGE_CHOICES, help_text="Programming language of the code.")

    post_processor_direct_value = models.CharField(
        max_length=500, default="", blank=True)

    apis_used = models.TextField(
        default="", null=True, blank=True, help_text="Post processor apis used")

    is_original_message_required = models.BooleanField(
        default=False, help_text="Decides whether show translated message or original message")

    class Meta:
        verbose_name = "Processor"
        verbose_name_plural = "Processor"

    def __str__(self):
        return self.name

    def save(self, from_backend=False, *args, **kwargs):
        # from_backend: This is true if you are trying to create an object from
        # console, false otherwise.
        if from_backend:
            super(Processor, self).save(*args, **kwargs)
        else:
            try:
                processor_objs = Processor.objects.filter(name=self.name)
                if len(processor_objs) > 0:
                    raise ValidationError('This name already exists.')
            except Exception:
                logger.info("Matching processor name doesn't exists", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            super(Processor, self).save(*args, **kwargs)


class ApiTree(models.Model):

    name = models.CharField(default="", max_length=100,
                            help_text="API tree name")

    api_caller = models.TextField(default="def f():\n    return response")

    is_cache = models.BooleanField(
        default=False, help_text="Designates whether caching is allowed or not.")

    cache_variable = models.CharField(
        max_length=100, null=True, blank=True, help_text="Cache variable")

    users = models.ManyToManyField(
        User, blank=True, help_text="Specific users for Api tree.")

    processor_lang = models.CharField(max_length=256,
                                      default="1",
                                      null=True,
                                      blank=False,
                                      choices=LANGUAGE_CHOICES, help_text="Programming language of the code.")
    apis_used = models.TextField(default="", null=True, blank=True)

    class Meta:
        verbose_name = "API Tree"
        verbose_name_plural = "API Trees"

    def __str__(self):
        return self.name

    def save(self, from_backend=False, *args, **kwargs):
        # from_backend: This is true if you are trying to create an object from
        # console, false otherwise.
        if from_backend:
            super(ApiTree, self).save(*args, **kwargs)
        else:
            try:
                api_tree_objs = ApiTree.objects.filter(name=self.name)
                if len(api_tree_objs) > 0:
                    raise ValidationError('This name already exists.')
            except Exception:
                logger.info("Matching processor name doesn't exists", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            super(ApiTree, self).save(*args, **kwargs)


class TrainingData(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    data_type = models.CharField(max_length=256,
                                 null=False,
                                 blank=False,
                                 choices=TRAINING_DATA_TYPE_CHOICES,
                                 help_text='Denotes whether training data is of intent level or tree level.')

    tree = models.ForeignKey(
        'Tree', null=True, blank=True, on_delete=models.SET_NULL)

    training_data = models.TextField(
        default="", help_text="Training data for semantic similarities.")

    def __str__(self):
        try:
            if self.data_type == "1":
                return str(self.bot.name) + " - " + str(self.data_type)
            else:
                return str(self.data_type) + "-" + str(self.tree.name)
        except Exception:
            return 'None'

    class Meta:
        verbose_name = "TrainingData"
        verbose_name_plural = "TrainingData"


class Tree(models.Model):

    name = models.CharField(default="", max_length=5000)

    multilingual_name = models.CharField(
        max_length=5000, blank=True, help_text="Multilingual name")

    response = models.ForeignKey(
        BotResponse, null=True, blank=True, on_delete=models.CASCADE, help_text="Bot Response")

    explanation = models.ForeignKey(
        Explanation, null=True, blank=True, on_delete=models.CASCADE)

    children = models.ManyToManyField(
        'Tree', blank=True, help_text="Specific child of this tree.")

    accept_keywords = models.TextField(default="", null=True, blank=True)

    short_name = models.CharField(default="", null=False, max_length=25, help_text="Short name for intent.")

    is_automatic_recursion_enabled = models.BooleanField(default=False)

    # choosen_file_type = models.TextField(default="", null=True, blank=True)

    pre_processor = models.ForeignKey(
        Processor, null=True, blank=True, related_name="pre_processor", on_delete=models.SET_NULL, help_text="Pre processor")

    post_processor = models.ForeignKey(
        Processor, null=True, blank=True, related_name="post_processor", on_delete=models.SET_NULL, help_text="Post processor")

    pipe_processor = models.ForeignKey(
        Processor, null=True, blank=True, related_name="pipe_processor", on_delete=models.SET_NULL, help_text="Pipe processor")

    api_tree = models.ForeignKey(
        ApiTree, blank=True, null=True, on_delete=models.SET_NULL, help_text="API Tree")

    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether tree is deleted or not. Select this instead of deleting the tree.")

    is_child_tree_visible = models.BooleanField(
        default=True, help_text="Child tree name are visible as choices or not.")
    is_go_back_enabled = models.BooleanField(
        default=False, help_text="Designates whether go back feature enabled or not.")

    is_confirmation_and_reset_enabled = models.BooleanField(
        default=False, help_text="Designates whether bot confirmation and reset intent enabled or not.")

    confirmation_reset_tree_pk = models.IntegerField(
        null=True, blank=True, help_text='Confirmation and Reset tree ID')

    flow_analytics_variable = models.CharField(
        max_length=5000, default="", help_text="Save flow analytics variable", blank=True)

    is_category_response_allowed = models.BooleanField(
        default=False, help_text="Designates whether category response is allowed or not.")

    is_last_tree = models.BooleanField(
        default=False, help_text="Check if it's the last tree of the flow")

    is_custom_order_selected = models.BooleanField(
        default=False, help_text="Designates whether custom order is selected for order of response")

    order_of_response = models.TextField(
        default="[]", help_text="Order of response for the child intent.")

    is_exit_tree = models.BooleanField(
        default=False, help_text="Designates whether it's exit tree for chatbot or not")

    enable_transfer_agent = models.BooleanField(
        default=False, help_text="Designates to handover to expert from bot")

    voice_bot_conf = models.TextField(default=json.dumps(
        TREE_LEVEL_VOICE_BOT_CONFIGURATIONS), help_text="Voice bot ralted configurations on tree level.")

    disposition_code = models.CharField(default="", max_length=50, help_text="This code is used to identify the node at which user has reached the flow in Voice campaigns.")

    enable_whatsapp_menu_format = models.BooleanField(default=False, help_text="This designates whether the interactive menu format is enabled or not.")

    whatsapp_short_name = models.CharField(max_length=30, null=True, blank=True, help_text="This is the text which will be shown on whatsapp interactive buttons.")

    whatsapp_description = models.CharField(max_length=80, null=True, blank=True, help_text="This is the text which will be shown under whatsapp interactive button.")

    is_catalogue_purchased = models.BooleanField(
        default=False, help_text="If enabled, user's latest whatsapp catalogue cart will be marked as purhcased if they reach this tree")

    def disable(self):  # noqa F811
        self.is_deleted = True
        self.save()

    def check_barge_in_enablement(self):
        try:
            return json.loads(self.voice_bot_conf)["barge_in"]
        except Exception:
            return False

    def get_whatsapp_short_name(self):
        try:
            if self.whatsapp_short_name:
                return str(self.whatsapp_short_name)
            
            if len(self.name) > 24:
                return self.name[0:22].strip() + ".."
            return self.name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_whatsapp_short_name! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        return "None"

    def get_whatsapp_description(self):
        try:
            if self.whatsapp_description:
                return str(self.whatsapp_description)
            
            if len(self.name) > 72:
                return self.name[0:70].strip() + ".."
            return self.name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_whatsapp_description! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        return "None"

    def save(self, *args, **kwargs):
        if self.name is not None and len(self.name) > self._meta.get_field('name').max_length:
            raise ValueError("Tree name length is greater then Max length - ",
                             self._meta.get_field('name').max_length)
        super(Tree, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Tree"
        verbose_name_plural = "Trees"

    def __str__(self):
        return self.name


@receiver(post_save, sender=Tree)
def create_tree_hash(sender, instance, **kwargs):
    try:
        is_intent = Intent.objects.filter(tree=instance)
        if not is_intent.exists():
            IntentTreeHash.objects.filter(
                tree=instance).delete()
            stem_words = get_stem_words_of_sentence(
                instance.name, None, None, None, None)
            stem_words.sort()
            stem_words_name = ' '.join(stem_words)
            hashed_name = hashlib.md5(stem_words_name.encode()).hexdigest()
            IntentTreeHash.objects.create(
                tree=instance, stem_words_name=stem_words_name, hash_value=hashed_name, is_tree=True, training_question=instance.name)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_tree_hash! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


@receiver(post_save, sender=Tree)
def update_training_data_for_advanced_nlp(sender, instance, **kwargs):
    try:
        sync_tree_object_training_data(instance, TrainingData, Config)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_tree_hash! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


class Data(models.Model):

    user = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.CASCADE)

    bot = models.ForeignKey(
        Bot, null=True, blank=True, on_delete=models.SET_NULL)

    variable = models.CharField(
        max_length=100, null=True, blank=True, help_text="Storing data model during flow.")

    value = models.TextField(null=True, blank=True,
                             help_text="Value for variable")

    is_cache = models.BooleanField(
        default=False, help_text="Designates whether cache should be stored or not")

    cached_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time of cache stored")

    class Meta:
        verbose_name = "Data"
        verbose_name_plural = "Data"

    def __str__(self):
        return self.variable

    def get_value(self):
        try:
            if self.variable == "attached_file_src":
                return self.value
            value = DecryptVariable(self.value)

            if value != "null":
                return value
            return self.value
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in get_value %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

            return self.value

    def save(self, *args, **kwargs):
        try:
            if self.bot and self.bot.masking_enabled and self.value and self.variable != "attached_file_src":
                custom_encrypt_obj = CustomEncrypt()

                self.value = custom_encrypt_obj.encrypt(self.value)

            super(Data, self).save(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in Save Data %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

            super(Data, self).save(*args, **kwargs)


class Config(models.Model):

    monthly_analytics_parameter = models.IntegerField(
        default=6, help_text="Last this much months analytics will be shown.")

    daily_analytics_parameter = models.IntegerField(
        default=7, help_text="Last this much days analytics will be shown.")

    top_intents_parameter = models.IntegerField(
        default=5, help_text="This much top intents will be shown.")

    sample_questions = models.TextField(default="{}", null=True, blank=True)

    app_url = models.CharField(
        max_length=200, default="http://localhost:8000", help_text="App url.")

    intent_not_found_response = models.TextField(
        default="Sorry. I do not understand what you mean. Please elaborate.", null=True, blank=True, help_text="Response by bot when intet is not found.")

    generic_error_response = models.TextField(
        default="Sorry. I've trouble fetching response. Please try again.", null=True, blank=True, help_text="Generic error message by bot.")

    site_title = models.CharField(
        max_length=100, default="EasyChat", help_text="Title of the site")

    prod = models.BooleanField(
        default=False, help_text="Designates whether it is in production or not.")

    is_feedback_required = models.BooleanField(
        default=False, help_text="Desginate whether feedback is required or not.")

    # is_attachment_required = models.BooleanField(default=False)

    # choosen_file_type = models.TextField(default="", null=True, blank=True)

    allow_bot_switch = models.BooleanField(
        default=False, help_text="Designates whether bot switch is allowed or not.")

    cached_duration = models.IntegerField(
        default=300, help_text="Cache duration is seconds.")  # In seconds

    languages_supported = models.ManyToManyField(
        'Language', blank=True, help_text="Specific languages supported by bot.")

    no_of_bots_allowed = models.IntegerField(
        default=1, help_text="Maximum number of bots that can be created.")

    is_bot_shareable = models.BooleanField(
        default=True, help_text="Designated whether bot is sharable or not.")

    is_google_search_allowed = models.BooleanField(
        default=False, help_text="Designates whether google search is allowed or not.")

    is_auto_correct_required = models.BooleanField(
        default=False, help_text="Designates whether auto correct is allowed or not.")

    show_licence = models.BooleanField(default=False)

    show_intent_threshold_functionality = models.BooleanField(default=False)
    autocorrect_replace_space = models.CharField(
        max_length=50, blank=True, default="", help_text='Characters in this text field will be replaced by space. All characters which are not in this and do_nothing list will be replaced by blank.')

    autcorrect_do_nothing = models.CharField(max_length=50, blank=True, default=".\-:@+,#%&!",
                                             help_text='Characters in this text field will be kept as it is. All characters which are not in this and replace_space list will be replaced by blank.')

    autoreply_email = models.CharField(
        max_length=100, blank=True, help_text="Autoreply email", default=settings.EMAIL_HOST_USER)

    autoreply_email_password = models.CharField(
        max_length=100, blank=True, help_text="Autoreply email password", default=settings.EMAIL_HOST_PASSWORD)

    is_data_collection_on = models.BooleanField(
        default=False, help_text="data collection option will not be present in console if it is False.")

    is_data_drive_on = models.BooleanField(
        default=False, help_text="data drive option will not be present in console if it is False.")

    is_feedback_on = models.BooleanField(
        default=False, help_text="feedback option will not be present in console if it is False.")

    is_sso_on = models.BooleanField(
        default=False, help_text="SSO option will not be present in console if it is False.")

    is_package_installer_on = models.BooleanField(
        default=False, help_text="Package installer feature in intent advanced setting should be visible or not.")

    is_whatsapp_simulator_on = models.BooleanField(
        default=False, help_text="WhatsApp simulator off if False else on")

    image_compress_size = models.IntegerField(
        default=512, help_text="Defines size of image after it is compressed.")

    system_commands = models.TextField(
        null=True, default="['os.system', 'subprocess', 'import threading', 'threading.Thread', 'ssh']")

    static_file_version = models.FloatField(
        default=1.0, help_text="Version of static files (js and css) in bot")

    percentage_threshold_for_message_history = models.IntegerField(
        default=25, help_text="This is used to distinguish flagged queries from normal queries.")

    repeat_event_variations = models.TextField(default=json.dumps(
        {"items": REPEAT_EVENT_TRAINING_SENTENCES}), null=True, blank=True)

    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Config"

    def __str__(self):
        return "Config"


class Category(models.Model):

    name = models.CharField(max_length=100, null=False,
                            blank=False, help_text="Category name.")

    bot = models.ForeignKey(Bot, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class MISDashboard(models.Model):

    date = models.DateTimeField(default=timezone.now)

    creation_date = models.DateField(
        default=now, db_index=True, help_text="Date of creation of current MIS")

    user_id = models.CharField(
        max_length=100, db_index=True, help_text="User id")

    session_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Session id")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)

    message_received = models.TextField(
        null=True, help_text="Message received by bot.")

    selected_language = models.ForeignKey("Language", null=True, blank=True,
                                          on_delete=models.SET_NULL)

    sentiment = models.TextField(
        null=True, help_text="Sentiment")

    bot_response = models.TextField(
        null=True, help_text="Response given by bot.")

    intent_name = models.TextField(db_index=True,
                                   max_length=100, null=True, help_text="Intent name")

    training_question = models.CharField(
        max_length=200, default="", help_text="Training question which triggered intent if any")

    match_percentage = models.IntegerField(
        default=-1, help_text="Match percentage of query w.r.t training question if any")

    recommendations = models.TextField(
        max_length=1024, null=True, default="[]", help_text="Recommendations")

    choices = models.TextField(
        max_length=1024, null=True, default="[]", help_text="Choices")

    category_name = models.TextField(
        null=True, default="", help_text="Category name.")

    feedback_info = models.TextField(
        default="{\"is_helpful\":0,\"comments\":\"\"}", max_length=100, null=True, help_text="Feedback by user.")

    small_talk_intent = models.BooleanField(
        default=False, help_text="Designates whether the intent is small talk intent or not.")

    channel_name = models.TextField(null=True, help_text="Channel name.")

    action_taken = models.TextField(
        default="{}", null=True, blank=True, verbose_name="Action Taken")

    api_request_packet = models.TextField(
        null=True, help_text="API request packet")

    api_response_packet = models.TextField(
        null=True, help_text="API response packet")

    api_request_parameter_used = models.TextField(
        null=True, help_text="API request used parameters")

    api_response_parameter_used = models.TextField(
        null=True, help_text="API response used parameters")

    window_location = models.CharField(
        max_length=500, null=True, blank=True, help_text="Source location")

    attachment = models.CharField(
        max_length=1000, null=True, blank=True, help_text="Attachment")

    response_json = models.TextField(
        default="", null=True, help_text="JSON of response")

    widgets = models.TextField(
        max_length=1024, null=True, default="[]", help_text="Widgets")

    is_helpful_field = models.CharField(
        default=0, max_length=2, help_text="Feedback helpful")

    feedback_comment = models.TextField(
        max_length=5000, null=True, default="", help_text="Feedback by user")

    intent_recognized = models.ForeignKey(Intent, null=True, blank=True,
                                          on_delete=models.SET_NULL)

    status = models.CharField(max_length=1,
                              default="2",
                              null=True,
                              blank=True,
                              choices=ROLES_MIS,
                              help_text='Status is for whether marked unanswered or no')
    form_data_widget = models.CharField(
        max_length=500000, default="", blank=True, help_text='')

    is_unidentified_query = models.BooleanField(
        default=False, help_text="Designates whether the query is unidentified or not")

    client_city = models.TextField(
        null=True, default="", help_text="Client city")

    client_state = models.TextField(
        null=True, default="", help_text="Client state")

    client_pincode = models.TextField(
        null=True, default="", help_text="Client pincode")

    is_manually_typed_query = models.BooleanField(
        default=True, help_text="Weather query is manually typed by user.")

    flagged_queries_positive_type = models.CharField(max_length=1, null=True, blank=True, choices=FLAGGED_QUERY_TYPES,
                                                     help_text="It represents if response given is False Positive or Not False Positive.")

    is_session_started = models.BooleanField(
        default=True, help_text="Weather the session is started or not (this is for whatsapp session management )")

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL)

    is_intiuitive_query = models.BooleanField(
        default=False, help_text="Whether the current message is intuitive query or not")

    is_business_initiated_session = models.BooleanField(
        default=False, help_text="Designates whether the chat was initiated by business end")

    is_mobile = models.BooleanField(
        default=False, help_text="Designates whether the chat was initiated by mobile or desktop")

    is_session_blocked = models.BooleanField(default=False, help_text="This designates if the session was blocked or not.")

    class Meta:
        verbose_name = "MISDashboard"
        verbose_name_plural = "MISDashboard"
        ordering = ["-pk"]

    def is_helpful(self):
        mis_objs = MISDashboard.objects.filter(
            date__gte=self.date, user_id=self.user_id).order_by('pk')
        if len(mis_objs) > 1:
            if mis_objs[1].get_message_received().lower() == "helpful":
                return True
        return False

    def is_unhelpFul(self):  # noqa: N802
        mis_objs = MISDashboard.objects.filter(
            date__gte=self.date, user_id=self.user_id).order_by('pk')
        if len(mis_objs) > 1:
            if mis_objs[1].get_message_received().lower() == "unhelpful":
                return True
        return False

    def get_feedback_info(self):
        return json.loads(self.feedback_info)

    def get_datetime(self):
        try:
            import pytz
            est = pytz.timezone(settings.TIME_ZONE)
            return self.date.astimezone(est).strftime("%d %b %Y %I:%M %p")
        except Exception:
            return self.date.strftime("%d %b %Y %I:%M %p")

    def get_user_id(self):
        return self.user_id

    def get_bot_obj(self):
        return self.bot

    def get_message_received(self):
        try:
            message_received = DecryptVariable(self.message_received)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Get Message Recieved %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            message_received = self.message_received
        if self.form_data_widget != "":
            message_received = "Form Data Filled"
        return message_received

    def get_intent_obj(self):
        intent_name = self.intent_name
        try:
            intent_objs = Intent.objects.filter(
                name=intent_name, bots__in=[self.bot], is_deleted=False).distinct()
            if len(intent_objs) > 0:
                return intent_objs[0]
        except Exception:  # noqa: F841
            pass
        return None

    def get_bot_response(self):
        # log_filter_obj = SensitiveDataFilter()
        try:
            bot_response = DecryptVariable(self.bot_response)

            from EasyChatApp.utils_validation import EasyChatInputValidation
            validation_obj = EasyChatInputValidation()
            bot_response = validation_obj.remo_html_from_string(bot_response)

            # bot_response = log_filter_obj.hide_sensitive_text(bot_response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Get Message Recieved %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            # bot_response = log_filter_obj.hide_sensitive_text(self.bot_response)
            bot_response = self.bot_response
        import re
        bot_response = bot_response.replace("<ul>", "<ul class='bullet'>")
        bot_response = bot_response.replace("<ol>", "<ol class='num'>")
        bot_response = bot_response.replace(
            "<table>", "").replace("</table>", "")
        bot_response = bot_response.replace("<td>", "").replace("</td>", "")
        bot_response = bot_response.replace("<tr>", "").replace("</tr>", "")

        return bot_response

    def get_bot_response_with_html_tags_intact(self):
        try:
            bot_response = DecryptVariable(self.bot_response)
            # bot_response = log_filter_obj.hide_sensitive_text(bot_response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Get Message Recieved %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            # bot_response = log_filter_obj.hide_sensitive_text(self.bot_response)
            bot_response = self.bot_response

        return bot_response

    def get_intent_name_for_profanity_or_emoji_response(self):

        if not self.intent_name:
            return self.intent_name

        intent_name_to_be_checked = self.intent_name.lower().strip().replace(" ", "_")
        if intent_name_to_be_checked == "emoji_bot_response" or intent_name_to_be_checked == "profanity_bot_response":
            if not self.intent_recognized:
                return self.intent_name

        return ""

    def get_channel_name(self):
        return self.channel_name

    def get_channel_redirection_url_name(self):
        channel_name = self.channel_name
        channel_name = channel_name.lower()
        if channel_name == "googlebusinessmessages":
            channel_name = "google-buisness-messages"
        if channel_name == "googlehome":
            channel_name = "google-assistant"
        if channel_name == "microsoft":
            channel_name = "microsoft-teams"
        return channel_name

    def get_api_request_packet(self):
        return self.api_request_packet

    def get_api_response_packet(self):
        return self.api_response_packet

    def get_feedback_comments(self):
        comments = "No comments"
        try:
            comments = json.loads(self.feedback_info)["comments"]
        except Exception:
            pass
        return comments

    def is_small_talk_intent(self):
        intent_obj = self.get_intent_obj()
        if intent_obj != None:
            return intent_obj.is_small_talk

        return False

    def __str__(self):
        return "MISDashboard"

    def get_action_taken_list(self):
        import json
        action_taken_list = json.loads(self.action_taken)
        return action_taken_list

    def set_action_taken_list(self, intent_obj, action):
        import json
        action_taken_dict = json.loads(self.action_taken)
        # intent_obj = Intent.objects.get(pk=int(intent_obj_pk))
        if action.strip().lower() == "match":
            action_taken_dict["match"] = {}
            action_taken_dict["match"]["intent"] = intent_obj.pk
            action_taken_dict["match"][
                "message"] = '<a '
            action_taken_dict["match"][
                "message"] += '" class="tooltipped" data-position="bottom" data-tooltip="'
            action_taken_dict["match"]["message"] += str(intent_obj.name)
            action_taken_dict["match"]["message"] += '">'
            action_taken_dict["match"]["message"] += "Added to intent"
            action_taken_dict["match"]["message"] += '</a>'
            self.action_taken = json.dumps(action_taken_dict)
            self.save()

    def get_sentiment(self):
        return self.sentiment

    def get_whatsapp_menu_section_list(self):
        try:
            response_json = json.loads(self.response_json)
            if "whatsapp_menu_sections" in response_json["response"]:
                return response_json["response"]["whatsapp_menu_sections"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_whatsapp_menu_section_list %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return []


@receiver(post_save, sender=MISDashboard)
def add_sentiment(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        mis_obj = MISDashboard.objects.get(pk=instance.pk)
        mis_obj.sentiment = predict_sentiment(mis_obj.get_message_received())
        mis_obj.save()


class TagMapper(models.Model):

    display_variable = models.CharField(
        max_length=100, blank=False, null=False)

    alias_variable = models.CharField(max_length=100, blank=False, null=False)

    description = models.CharField(max_length=150, blank=True, null=True)

    api_tree = models.ForeignKey(
        'ApiTree', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "TagMapper"
        verbose_name_plural = "TagMapper"

    def __str__(self):
        return self.display_variable

    def save(self, *args, **kwargs):
        if self.description == "" or self.description == None:
            self.description = self.display_variable
        super(TagMapper, self).save(*args, **kwargs)


class Authentication(models.Model):

    name = models.CharField(max_length=50, null=False,
                            blank=False, help_text="Authentication name.")

    bot = models.ForeignKey(
        Bot, on_delete=models.CASCADE, null=True, blank=True)

    tree = models.ForeignKey(
        Tree, on_delete=models.CASCADE, null=True, blank=True)

    auth_time = models.IntegerField(
        default=300, help_text="Authentication time in seconds.")  # Seconds

    class Meta:
        verbose_name = "Authentication"
        verbose_name_plural = "Authentications"

    def __str__(self):
        return self.name


class UserAuthentication(models.Model):

    user = models.ForeignKey(
        Profile, null=False, blank=False, on_delete=models.CASCADE)

    auth_type = models.ForeignKey(
        Authentication, null=False, blank=False, on_delete=models.CASCADE, help_text="Authentication type.")

    start_time = models.DateTimeField(
        default=timezone.now, help_text="Start date and time")

    unique_token = models.CharField(max_length=500, null=True, blank=False,
                                    help_text="Unique parameters for user authentication, it may be mobile number, loand number, client id etc")

    last_update_time = models.DateTimeField(
        default=timezone.now, help_text="Start date and time")

    user_params = models.TextField(default="{}", help_text="User params.")

    class Meta:
        verbose_name = 'UserAuthentication'
        verbose_name_plural = 'UserAuthentication'

    def __str__(self):
        return self.user.user_id


class Language(models.Model):

    lang = models.CharField(max_length=10, null=False,
                            blank=False, help_text="Language", unique=True)

    display = models.CharField(
        max_length=40, null=True, blank=True, unique=True)

    name_in_english = models.CharField(
        max_length=40, null=True, blank=True, unique=True)

    language_script_type = models.CharField(default="ltr", max_length=10, null=True, blank=True,
                                            help_text="This field designates whether the language is left to right typing or right to left typing type.")

    def __str__(self):
        return self.lang

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = "Languages"


class TestCase(models.Model):

    sentence = models.TextField(
        default="{\"sentence_list\":[]}", null=True, blank=True)

    is_active = models.TextField(
        default="{\"is_active_list\":[]}", null=True, blank=True)

    intent = models.ForeignKey(
        'Intent', on_delete=models.CASCADE, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + ' ' + str(self.intent)

    # to be exposed

    def get_is_active_list(self):
        return json.loads(self.is_active)["is_active_list"]

    def get_list(self):
        return json.loads(self.sentence)["sentence_list"]
        # deserialize the sentence column
        # return a list

    def get_active_sentence_list(self):
        is_active_list = self.get_is_active_list()
        complete_sentence_list = self.get_list()
        sentence_list = []
        for iterator in range(len(is_active_list)):
            if is_active_list[iterator] == True:
                sentence_list.append(complete_sentence_list[iterator])
        return sentence_list

    # not to be exposed

    def set_list(self, sentence_list):
        self.sentence = json.dumps({"sentence_list": sentence_list})
        # serialize the sentences
        # save it in sentence

    def set_is_active_list(self, is_active_list):
        self.is_active = json.dumps({"is_active_list": is_active_list})

    # to be exposed

    def add_sentence(self, sentence):
        sentences = self.get_list()
        is_active_list = self.get_is_active_list()

        sentences.append(sentence)
        is_active_list.append(True)

        self.set_list(sentences)

        self.set_is_active_list(is_active_list)

    def get_index(self, sentence):
        sentences = self.get_list()
        return sentences.index(sentence)

    def remove_index(self, index):
        sentences = self.get_list()
        is_active_list = self.get_is_active_list()
        del sentences[index]
        del is_active_list[index]

        self.set_list(sentences)

        self.set_is_active_list(is_active_list)

    def change_is_active(self, index, is_active_value):
        is_active_list = self.get_is_active_list()
        is_active_list[index] = is_active_value

        self.set_is_active_list(is_active_list)

    # to be exposed
    def delete_sentence(self, sentence):
        sentences = self.get_list()
        sentences.remove(sentence)
        self.set_list(sentences)

    def delete_all_sentences(self):
        self.set_list([])

    def check_sentence(self, sentence):
        if self.intent.get_intent(sentence).pk == self.intent.pk:
            return True
        return False

    def check_sentences(self, sentences):
        return [self.check_sentence(sentence) for sentence in sentences]

    def get_failed_sentences(self):
        sentences = self.get_list()
        failed_sentences = []
        for sentence in sentences:
            if not self.check_sentence(sentence):
                failed_sentences.append(sentence)

        return failed_sentences


class TrainingTemplateSentence(models.Model):
    sentence = models.CharField(
        max_length=200, blank=True, null=True, help_text="Training template sentence.")

    def __str__(self):
        return self.sentence


class TrainingTemplate(models.Model):
    sentences = models.ManyToManyField(
        'TrainingTemplateSentence', blank=True, help_text="Specific sentences for training template.")

    no_of_vars = models.IntegerField(
        default=1, help_text="No of variables in a single sentence")

    def __str__(self):
        return self.sentences.all()[0].sentence


class ProcessorValidator(models.Model):
    name = models.CharField(max_length=200, blank=True,
                            null=True, help_text="Validator name.")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    processor = models.ForeignKey(
        Processor, null=True, blank=True, on_delete=models.CASCADE, help_text="Processor function")

    def __str__(self):
        return self.name


class Feedback(models.Model):
    user_id = models.CharField(max_length=100, help_text="User id")

    session_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Session id")
    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE, help_text="Bot whose feedback is given.")

    channel = models.ForeignKey(Channel, null=True, blank=True,
                                on_delete=models.SET_NULL, help_text="Channel on which feedback is given.")

    rating = models.IntegerField(
        default=0, db_index=True, help_text="Rating on a scale of 0 to 10")
    comments = models.TextField(default="", help_text="Feedback comment.")

    date = models.DateTimeField(
        default=timezone.now, help_text="Date and time of feedback.")

    phone_number = models.TextField(
        default="", help_text="Feedback phone number")
    country_code = models.TextField(
        null=True, blank=True, default="", help_text="Feedback country code")
    email_id = models.TextField(
        default="", help_text="Feedback email id")
    all_feedbacks = models.CharField(
        default="", blank=True, null=True, max_length=500000)

    scale_rating_5 = models.BooleanField(
        default=False, blank=False, null=False, help_text="Whether Csat rating scale is 5 or 4")

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def save(self, *args, **kwargs):
        super(Feedback, self).save(*args, **kwargs)

    def __str__(self):
        return self.user_id

    def get_datetime(self):
        try:
            import pytz
            est = pytz.timezone(settings.TIME_ZONE)
            return self.date.astimezone(est).strftime("%d %b %Y %I:%M %p")
        except Exception:
            return self.date.strftime("%d %b %Y %I:%M %p")

    def get_csat_score_str(self):
        try:
            csat_score = str(self.rating)
            if self.scale_rating_5:
                csat_score = csat_score + "/" + "5"
            else:
                csat_score = csat_score + "/" + "4"
            return csat_score
        except Exception:
            return "0"


class WordDictionary(models.Model):

    word_dict = models.TextField(
        default="{\"items\":[]}", help_text="Word Dictionary.")

    bot = models.ForeignKey(
        Bot, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "WordDictionary"
        verbose_name_plural = "WordDictionary"

    def __str__(self):
        return "WordDictionary"


class EasyChatDrive(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    media_name = models.CharField(
        max_length=200, null=True, blank=True, help_text="Uploaded media name.")

    media_url = models.TextField(
        default="", null=True, blank=True, help_text="Uploaded media url.")

    media_type = models.CharField(
        max_length=1, null=True, blank=True, choices=MEDIA_TYPES, help_text="Uploaded media type")

    class Meta:
        verbose_name = 'EasyChatDrive'
        verbose_name_plural = 'EasyChatDrive'

    def get_media_type(self):
        return MEDIA_TYPE_DICT[self.media_type]

    def __str__(self):
        return self.user.username


def get_intent_related_tree_pks_list(parent_tree_pk):
    try:
        pk_list = [parent_tree_pk]
        # parent_tree_obj = Tree.objects.get(
        #     pk=int(parent_tree_pk), is_deleted=False)
        # child_pk_list = list(
        #     parent_tree_obj.children.values_list('pk', flat=True))

        # pk_list = [int(parent_tree_pk)]
        # for pk in child_pk_list:
        #     pk_list += get_intent_related_tree_pks_list(pk)

        return pk_list
    except Exception as e:  # noqa: F841
        logger.error("Error in get_intent_related_tree_pks_list: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return []


class AuditTrail(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    action = models.CharField(max_length=2, null=False,
                              choices=AUDIT_TRAIN_ACTIONS, help_text="Action by user.")

    datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time of action.")

    data = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        return self.user.username + " - " + self.action

    def get_action(self):
        if self.action == FAQ_EXCEL_UPLOADED_ACTION:
            return "<span style=\"font-weight:bold\">" + json.loads(self.data)["action"] + "</span> Intents Uploaded by Excel"

        return AUDIT_TRAIN_ACTION_DICT[self.action]

    def get_description(self):
        description = []
        try:
            data = json.loads(self.data)
            description = data["change_data"]
        except Exception:
            pass

        return description

    def get_redirect_data(self):
        try:
            if self.action == FAQ_EXCEL_UPLOADED_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=int(data["bot_pk"]))
                url = "Bot: <a target=\"_blank\" href=\"/chat/intent?bot_pk=" + \
                    str(bot_obj.pk) + "\">" + str(bot_obj.name) + "</a>" + \
                    "<a href=\"" + \
                    data[
                        "filepath"] + "\" class=\"black-text white right\"><i class=\"material-icons black-text inline-icon\">file_download</i>"
                return url

            if self.action == DELETE_INTENT_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=int(data["bot_pk"]))
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == CREATE_INTENT_FROM_FAQ_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=int(data["bot_pk"]))
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == CREATE_INTENT_ACTION or self.action == MODIFY_INTENT_ACTION:
                data = json.loads(self.data)
                intent_obj = Intent.objects.get(pk=int(data["intent_pk"]))
                url = "Intent: <a target=\"_blank\" href=\"/chat/edit-intent/?intent_pk=" + \
                    str(intent_obj.pk) + "&selected_language=en\">" + \
                    str(intent_obj.name) + "</a>"
                return url

            if self.action == SHARE_BOT_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=int(data["bot_pk"]))
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                user_id_list = data["user_id_list"]

                for user_id in user_id_list:
                    user_obj = User.objects.get(pk=int(user_id))
                    url += '<br> Manager: ' + str(user_obj.username)
                return url

            if self.action == UNSHARE_BOT_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                user_obj = User.objects.get(pk=data["user_id"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                url += '<br> Manager: ' + str(user_obj.username)
                return url

            if self.action == USER_LOGGED_IN:
                data = json.loads(self.data)
                user_obj = User.objects.get(pk=data["user_id"])
                url = 'User: ' + str(user_obj.username)
                return url

            if self.action == USER_LOGGED_OUT:
                data = json.loads(self.data)
                user_obj = User.objects.get(pk=data["user_id"])
                url = 'User: ' + str(user_obj.username)
                return url

            if self.action == DELETE_BOT_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot Name: ' + str(bot_obj.name)
                return url

            if self.action == CREATE_BOT_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == EXPORT_BOT_AS_JSON_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == IMPORT_BOT_FROM_JSON_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == EXPORT_BOT_AS_ZIP_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == IMPORT_BOT_FROM_ZIP_ACTION:
                data = json.loads(self.data)
                bot_obj = Bot.objects.get(pk=data["bot_pk"])
                url = 'Bot: <a target="_blank" href="/chat/intent?bot_pk=' + \
                    str(bot_obj.pk) + '"">' + str(bot_obj.name) + '</a>'
                return url

            if self.action == EDIT_PROCESSOR_ACTION:
                data = json.loads(self.data)
                processor = data["processor"]
                name = data["processor_name"]
                url = 'Processor Edited<br>Processor: ' + \
                    processor + '<br>Processor name: ' + name
                return url

            if self.action == CREATE_PROCESSOR_ACTION:
                data = json.loads(self.data)
                processor = data["processor"]
                name = data["processor_name"]
                url = 'New processor created<br>Processor type: ' + \
                    processor + '<br>Processor name: ' + name
                return url

            if self.action == DELETE_PROCESSOR_ACTION:
                data = json.loads(self.data)
                processor = data["processor"]
                name = data["processor_name"]
                url = 'Deleted processor<br>Processor type: ' + \
                    processor + '<br>Processor name: ' + name
                return url

        except Exception:
            return ""

        return ""

    def get_user_details(self):
        details = []
        try:
            if self.action == USER_LOGGED_IN:
                data = json.loads(self.data)
                details.append(data["browser"])
                details.append(data["source_ip"])
            return details
        except Exception:
            return details

    class Meta:
        verbose_name = 'AuditTrail'
        verbose_name_plural = 'AuditTrail'
        ordering = ['-pk']


class Supervisor(models.Model):

    supervisor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="supervisor", help_text="Supervisor id")

    managers = models.ManyToManyField(
        User, blank=True, related_name="managers", help_text="Specific managers who is supervised by this supervisor")

    def __str__(self):
        return self.supervisor.username

    def get_managers_list(self):
        return self.managers.all()

    class Meta:
        verbose_name = 'Supervisor'
        verbose_name_plural = 'Supervisors'


class CustomUser(User):

    user_params = models.TextField(null=True,
                                   blank=True)

    def save(self, *args, **kwargs):
        if self.pk == None:
            self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(CustomUser, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"


##################### LiveChat ##################

class CustomerCareAgent(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="Customer Care Agent")

    is_active = models.BooleanField(
        default=False, help_text="Designates whether agent is active or not.")

    no_of_customers = models.IntegerField(
        default=0, help_text="This much customers is assigned to this agent.")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Customer Care Agent"
        verbose_name_plural = "Customer Care Agents"


class LiveChatSession(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    customer_care_agent = models.ForeignKey(
        CustomerCareAgent, on_delete=models.CASCADE, help_text="Customer Care Agent of live chat session.")

    created_datetime = models.DateTimeField(
        default=now, help_text="Live chat session date and time.")

    is_active = models.BooleanField(
        default=True, help_text="Designates whether session is active or not.")

    message_history = models.TextField(
        null=True, blank=True, help_text="Live chat session message history.")

    class Meta:
        verbose_name = "LiveChat Session"
        verbose_name_plural = "LiveChat Sessions"

    def __str__(self):
        return str(self.pk)


class TimeSpentByUser(models.Model):

    user_id = models.CharField(
        max_length=100, db_index=True, help_text="User id")

    session_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Session id")

    start_datetime = models.DateTimeField(null=True, blank=True,
                                          default=now, help_text="Date and time when user start using bot.")

    end_datetime = models.DateTimeField(null=True, blank=True,
                                        default=now, help_text="Date and time when user end using bot.")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    total_time_spent = models.IntegerField(
        default=0, help_text="Total time spent in seconds")

    web_page = models.TextField(
        default="", null=True, blank=True, help_text="Web page where user was using the bot")

    web_page_source = models.TextField(
        default="", null=True, blank=True, help_text="Source from where web_page was redirected")

    class Meta:
        verbose_name = "TimeSpentByUser"
        verbose_name_plural = "TimeSpentByUsers"

    def time_diff(self):
        diff = (self.end_datetime - self.start_datetime).total_seconds()
        return diff

    def save(self, *args, **kwargs):
        super(TimeSpentByUser, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user_id)


class FormAssist(models.Model):

    tag_id = models.CharField(
        max_length=100, null=False, blank=False, help_text="Form field tag id.")

    intent = models.ForeignKey(
        Intent, null=True, blank=True, on_delete=models.CASCADE, help_text="Form assist intent for the particular tag id.")

    bot = models.ForeignKey(
        Bot, null=True, on_delete=models.CASCADE, help_text="Form assist bot.")

    popup_timer = models.IntegerField(
        default=10, help_text='Form assist popup timer specific to this field.')

    def __str__(self):
        return self.bot.name + " - " + self.tag_id + " - " + self.intent.name

    class Meta:
        verbose_name = 'FormAssist'
        verbose_name_plural = 'FormAssists'


class ServiceRequest(models.Model):

    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, help_text="User")

    customer_name = models.CharField(
        max_length=100, null=False, blank=False, help_text="Name of the customer.")

    request = models.TextField(default="")

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,
                            blank=False, null=True, help_text="Bot")

    def __str__(self):
        return self.customer_name

    class Meta:
        verbose_name = 'ServiceRequest'
        verbose_name_plural = 'ServiceRequests'

    def get_domains(self):
        domains = self.request.split(",")
        try:
            domains.remove(",")
        except Exception:
            pass
        return domains


class EasyChatDataCollect(models.Model):

    collect_form_data = models.TextField(
        default="[]", null=True, blank=True, help_text="Data collected from form.")

    bot = models.ForeignKey(Bot, null=True, on_delete=models.CASCADE)

    form = models.ForeignKey('EasyChatDataCollectForm',
                             null=True, on_delete=models.CASCADE, help_text="Form from where data is collected")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bot.name

    class Meta:
        verbose_name = 'EasyChatDataCollectEntry'
        verbose_name_plural = 'EasyChatDataCollectEntries'

    def get_datetime(self):
        import pytz
        est = pytz.timezone(settings.TIME_ZONE)
        return self.updated_at.astimezone(est).strftime("%d %b %Y %I:%M %p")


class EasyChatDataCollectForm(models.Model):

    form_ui_data = models.TextField(
        default="[]", null=True, blank=True, help_text="Form data.")

    bot = models.ForeignKey(Bot, null=True, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bot.name

    class Meta:
        verbose_name = 'EasyChatDataCollectForm'
        verbose_name_plural = 'EasyChatDataCollectForm'

    def get_datetime(self):
        import pytz
        est = pytz.timezone(settings.TIME_ZONE)
        return self.updated_at.astimezone(est).strftime("%d %b %Y %I:%M %p")


class EasyChatTheme(models.Model):

    name = models.CharField(
        max_length=1000, null=True, blank=True, help_text="Theme Name")

    main_page = models.CharField(
        max_length=1000, null=True, blank=True, help_text="Home page")

    chat_page = models.CharField(
        max_length=1000, null=True, blank=True, help_text="Chatbot page")

    theme_image_paths = models.TextField(
        default="[]", null=True, blank=True, help_text="source of theme images in a list")

    def __str__(self):
        return self.main_page

    class Meta:
        verbose_name = 'EasyChatTheme'
        verbose_name_plural = 'EasyChatTheme'

    def get_theme_display_name(self):
        # this function return the name "theme_1 as Theme 1"
        name = self.name.split("_")
        display_name = " ".join(name)
        return display_name.capitalize()

    def get_first_image_src(self):

        image_path_list = json.loads(self.theme_image_paths)
        image_path = ""

        if len(image_path_list) < 1:
            image_path = DEFAULT_THEME_IMAGE_DICT[self.name][0]
        else:
            image_path = image_path_list[0]

        return image_path

    def get_second_image_src(self):

        image_path_list = json.loads(self.theme_image_paths)
        image_path = ""

        if len(image_path_list) < 2:
            image_path = DEFAULT_THEME_IMAGE_DICT[self.name][1]
        else:
            image_path = image_path_list[1]

        return image_path


class WhatsAppServiceProvider(models.Model):

    name = models.CharField(max_length=20, null=False, blank=False,
                            choices=WSP_CHOICES, help_text="Name of WhatsApp Service Provider")

    default_code_file_path = models.TextField(
        null=True, blank=True, help_text="Default code file path of the Whatsapp Service Provider")

    def __str__(self):
        # This method is defined by django itself.
        # This will return name associated with WSP_CHOICES value. (Format -
        # get_{attribut_name}_display)
        return str(self.get_name_display())

    class Meta:
        verbose_name = 'WhatsAppServiceProvider'
        verbose_name_plural = 'WhatsAppServiceProviders'


class WhatsAppWebhook(models.Model):

    function = models.TextField(
        null=False, blank=False, help_text="Write WhatsApp Webhook code here.")

    extra_function = models.TextField(
        null=True, blank=True, help_text='Write WhatsApp Webhook extra code here like: Push Notification etc')

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, help_text="WhatsApp bot", on_delete=models.SET_NULL,)

    whatsapp_service_provider = models.ForeignKey(
        WhatsAppServiceProvider, null=True, blank=True, on_delete=models.SET_NULL, help_text="Whatsapp service provider for whatsapp bot.")

    last_updated_timestamp = models.DateTimeField(
        default=timezone.now, help_text="This time gets updated to the time when user saves the webhook code.")

    users_active = models.ManyToManyField(
        User, help_text="This shows who is currently working on this webhook code.")

    def __str__(self):
        return str(self.bot.name) + "- WhatsAppWebhook - " + str(self.bot.pk)

    class Meta:
        verbose_name = 'WhatsAppWebhook'
        verbose_name_plural = 'WhatsAppWebhook'


class WhatsAppHistory(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, help_text="WhatsAppHistory bot", on_delete=models.SET_NULL)

    mobile_number = models.CharField(max_length=100, null=True, blank=True)

    request_packet = models.TextField(
        null=False, blank=False, help_text="Request Packet.")

    response_packet = models.TextField(
        null=False, blank=False, help_text="Response Packet.")

    received_datetime = models.DateTimeField(
        default=timezone.now, help_text="Received date and time.")

    response_datetime = models.DateTimeField(
        default=timezone.now, help_text="Response date and time")

    def __str__(self):
        return str(self.bot.name) + "- WhatsAppHistory - " + str(self.bot.pk)

    class Meta:
        verbose_name = "WhatsAppHistory"
        verbose_name_plural = "WhatsAppHistory"


class FormAssistAnalytics(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, help_text="Form assist bot", on_delete=models.SET_NULL)

    user_id = models.CharField(max_length=100, null=False, blank=False)

    form_assist_field = models.ForeignKey(
        FormAssist, on_delete=models.CASCADE, help_text="Form assit field")

    lead_datetime = models.DateTimeField(default=timezone.now)

    meta_data = models.TextField(null=True, blank=True)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    is_helpful = models.BooleanField(
        default=True, help_text="Designates whether the form assist response is helpful or not.")

    def __str__(self):
        return self.form_assist_field.tag_id

    class Meta:
        verbose_name = 'FormAssistAnalytics'
        verbose_name_plural = 'FormAssistAnalytics'


class APIElapsedTime(models.Model):

    user = models.ForeignKey('Profile', null=True,
                             blank=True, on_delete=models.CASCADE)
    bot = models.ForeignKey('Bot', null=True, blank=True,
                            on_delete=models.CASCADE)

    request_packet = models.TextField(default="{}",
                                      null=False, blank=False, help_text="Request Packet.")

    response_packet = models.TextField(default="{}",
                                       null=False, blank=False, help_text="Response Packet.")

    elapsed_time = models.FloatField(default=0.0)

    created_at = models.DateTimeField(default=timezone.now)

    api_name = models.CharField(
        max_length=100, help_text="Name of the processor api.")

    api_status = models.CharField(default="Passed",
                                  max_length=100, help_text="API status failed/passed")

    api_status_code = models.CharField(default="200",
                                       max_length=100, help_text="API status code 200/300/500")

    def __str__(self):
        return self.bot.name

    def get_request_packet(self):
        try:
            request_packet = json.loads(self.request_packet)
            return json.dumps(request_packet, indent=4)
        except Exception:
            return "None"

    def get_response_packet(self):
        try:
            response_packet = json.loads(self.response_packet)
            response_packet = json.dumps(response_packet, indent=4)
            return response_packet
        except Exception:
            return "None"

    def get_elapsed_time(self):
        try:
            return round(self.elapsed_time, 3)
        except Exception:
            return self.elapsed_time

    def get_easychat_datetime(self):
        try:
            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            tz = self.created_at.astimezone()

            if tz.hour < 12:
                flag = "AM"
                hour1 = tz.hour
            elif tz.hour == 12:
                hour1 = tz.hour
                flag = "PM"
            else:
                hour1 = tz.hour - 12
                flag = "PM"

            if hour1 <= 9:
                hour2 = "0" + str(hour1)
            else:
                hour2 = str(hour1)

            if tz.minute <= 9:
                minute1 = "0" + str(tz.minute)
            else:
                minute1 = str(tz.minute)

            time1 = str(hour2) + ":" + str(minute1) + " " + flag

            return time1 + ", " + self.created_at.date().strftime('%d-%b-%Y')
        except Exception:
            return self.created_at

    class Meta:
        verbose_name = "APIElapsedTime"
        verbose_name_plural = "APIElapsedTimes"


class LeadGeneration(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, help_text="Lead generation bot.", on_delete=models.SET_NULL)

    date_time = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Lead date and time.")

    name = models.CharField(max_length=100, help_text="Name of the user.")

    email_id = models.CharField(max_length=200, help_text="Email of the user.")

    phone_no = models.CharField(
        max_length=100, help_text="Phone number of a user.")

    class Meta:
        verbose_name = "LeadGeneration"
        verbose_name_plural = "LeadGenerations"

    def __str__(self):
        return self.name + " - " + self.email_id


class SecuredLogin(models.Model):

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True)

    failed_attempts = models.IntegerField(
        default=0, help_text="This number of times user failed to login.")

    last_attempt_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Date and time of user last login attempt.")

    last_password_change_date = models.DateTimeField(default=timezone.now)

    previous_password_hashes = models.TextField(
        default='{"password_hash": []}', help_text='List of last 5 password hashes that user has used')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'SecuredLogin'
        verbose_name_plural = 'SecuredLogin'


class ResetPassword(models.Model):

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True)

    reset_pass_verifycode = models.CharField(max_length=200)

    failed_attempts = models.IntegerField(default=0)

    last_attempt_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    total_attempts = models.IntegerField(default=0)

    last_request_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    token = models.UUIDField(
        help_text='unique access token key', default=uuid.uuid4)

    is_password_reseted_succesfully = models.BooleanField(
        default=False, help_text='Whether Password for this reset password session is rested or not')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.last_attempt_datetime = timezone.now()
        return super(ResetPassword, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'ResetPassword'
        verbose_name_plural = 'ResetPassword'


class AccessType(models.Model):

    name = models.CharField(
        max_length=100, help_text="Name of access type")

    value = models.CharField(
        max_length=100, help_text="Value of access type", default="")

    class Meta:
        verbose_name = "AccessType"
        verbose_name_plural = "AccessType"

    def __str__(self):
        return self.name


class AccessManagement(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="user id")

    bot = models.ForeignKey(
        Bot, on_delete=models.CASCADE, help_text="bot id")

    access_type = models.ManyToManyField(
        AccessType, help_text="access type")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'AccessManagement'
        verbose_name_plural = 'AccessManagement'


class EmailConfiguration(models.Model):

    bot = models.ForeignKey(
        Bot, on_delete=models.CASCADE, help_text="bot id")

    email_freq = models.CharField(max_length=256,
                                  null=False,
                                  blank=False,
                                  default="1",
                                  choices=EMAIL_FREQ_CHOICES)

    email_address = models.TextField(
        default="[]", null=True, blank=True)

    chat_history = models.TextField(
        default="[]", null=True, blank=True)

    channel = models.TextField(
        default="[]", null=True, blank=True)

    analytics = models.TextField(
        default="[]", null=True, blank=True)

    bot_accuracy_threshold = models.TextField(
        default="0", null=True, blank=True)

    subject = models.TextField(
        default="", null=True, blank=True)

    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.bot.name

    class Meta:
        verbose_name = 'EmailConfiguration'
        verbose_name_plural = 'EmailConfigurations'


class PackageManager(models.Model):

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,
                            help_text='For which bot these package is required')

    request_user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='User requested for package installation', null=False, blank=False, related_name='request_user')

    approved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='User who approved request for installation', null=True, blank=True, related_name='approved_user')

    package = models.CharField(max_length=100, null=False, blank=False,
                               help_text='package which needs to be installed')

    description = models.CharField(
        max_length=1000, null=False, blank=False, help_text='Reason for package installation')

    request_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime of request for package installation')

    approved_datetime = models.DateTimeField(
        default=None, help_text='datetime of request approved', null=True, blank=True)

    status = models.CharField(max_length=20, choices=(
        ("approved", "approved"), ("denied", "denied")), null=True, blank=True)

    is_installed = models.BooleanField(
        default=False, help_text='Whether package is installed or not')

    def __str__(self):
        return self.request_user.username + " - " + self.package

    class Meta:
        verbose_name = 'PackageManager'
        verbose_name_plural = 'PackageManager'


class GeneralFeedBack(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="user id")

    description = models.TextField(blank=False, null=False)

    category = models.TextField(blank=False, null=False)

    priority = models.TextField(blank=False, null=False)

    screenshot = models.ImageField(
        upload_to=settings.IMAGE_UPLOAD_PATH, null=True, blank=True, help_text="Screenshot depicting problem")

    status = models.TextField(default="Open", blank=True)

    remarks = models.TextField(default="No Remarks", blank=True)

    added_datetime = models.DateTimeField(default=timezone.now)

    app = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'GeneralFeedback'
        verbose_name_plural = 'GeneralFeedback'

    def __str__(self):
        return self.description

    def get_user(self):
        return self.user

    def get_category(self):
        return self.category

    def get_priority(self):
        return self.priority

    def get_status(self):
        return self.status

    def get_remarks(self):
        return self.remarks

    def get_app(self):
        return self.app


class EasyChatMAil(models.Model):

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    api_name = models.CharField(
        max_length=256, blank=True, help_text='Name of failed API.')

    last_mail_sent_date = models.DateTimeField(default=timezone.now)

    mail_sent_to = models.TextField(
        default="{\"items\":[]}", blank=True, help_text='Email ID of the user to whom the mail sent on API failed event')

    mail_sent_from = models.CharField(max_length=256, null=True, blank=True,
                                      help_text='Email ID of the user from whom the mail sent on API failed event')

    class Meta:
        verbose_name = 'EasyChatMAil'
        verbose_name_plural = 'EasyChatMAils'

    def __str__(self):
        return self.api_name


class BrokenBotMail(models.Model):

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE, help_text="The bot associated with this object.")

    domain = models.CharField(max_length=512, null=True, blank=True,
                              help_text="domain name on which bot is broken")

    channel = models.ForeignKey(Channel, null=True, blank=True,
                                on_delete=models.SET_NULL, help_text="Channel on which bot is broken.")

    last_mail_sent_date = models.DateTimeField(
        default=timezone.now, help_text="Date time at which the last mail was sent")

    mail_sent_to = models.TextField(
        default="{\"items\":[]}", blank=True, help_text='Email ID of the user to whom the mail sent on bot broken event')

    mail_sent_from = models.CharField(max_length=256, null=True, blank=True,
                                      help_text='Email ID of the user from whom the mail sent on bot broken event')

    class Meta:
        verbose_name = 'BrokenBotMail'
        verbose_name_plural = 'BrokenBotMails'

    def __str__(self):
        return str(self.bot) + " - " + str(self.domain) + " - " + str(self.last_mail_sent_date)


class ExportMessageHistoryRequest(models.Model):

    request_datetime = models.DateTimeField(default=timezone.now)

    bot = models.ForeignKey(Bot, null=False, blank=False,
                            on_delete=models.CASCADE)

    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)

    filter_param = models.TextField(default="{}", null=False, blank=False)

    is_completed = models.BooleanField(default=False)

    request_type = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'ExportMessageHistoryRequest'
        verbose_name_plural = 'ExportMessageHistoryRequest'

    def __str__(self):
        return self.bot.name + " - " + self.user.username


class LiveChatBotChannelWebhook(models.Model):

    function = models.TextField(
        null=False, blank=False, help_text="Write Webhook code here.")

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            on_delete=models.CASCADE, blank=True, help_text="bot")

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE)

    whatsapp_service_provider = models.ForeignKey('LiveChatApp.LiveChatWhatsAppServiceProvider', null=True,
                                                  blank=True, on_delete=models.SET_NULL, help_text="Whatsapp service provider for whatsapp bot.")

    last_updated_timestamp = models.DateTimeField(
        default=timezone.now, help_text="This time gets updated to the time when user saves the webhook code.")

    users_active = models.ManyToManyField(
        User, help_text="This shows who is currently working on this webhook code.")

    def __str__(self):
        return str(self.bot.name) + "-" + str(self.channel.name) + "-Webhook-" + str(self.bot.pk)

    def save(self, *args, **kwargs):
        if self.function == "Please select bot, channel. And click on 'save' and Open same object to get sample code":
            if self.channel.name == "WhatsApp":
                self.function = LILVECHAT_WHATSAPP_WEBHOOK_SAMPLE
            elif self.channel.name == "Facebook":
                self.function = LILVECHAT_FACEBOOK_WEBHOOK_SAMPLE

        super(LiveChatBotChannelWebhook, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'LiveChatBotChannelWebhook'
        verbose_name_plural = 'LiveChatBotChannelWebhooks'


class AnalyticsMonitoringLogs(models.Model):
    monitoring_obj = models.ForeignKey('AnalyticsMonitoring', null=False, blank=False,
                                       on_delete=models.CASCADE)

    count_of_consecutive_anamoly = models.IntegerField(default=0)

    logs = models.TextField(
        default="{\"items\":[]}", blank=True)

    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'AnalyticsMonitoringLogs'
        verbose_name_plural = 'AnalyticsMonitoringLogs'

    def __str__(self):
        return self.monitoring_obj.bot.name


class AnalyticsMonitoring(models.Model):

    bot = models.ForeignKey(Bot, null=False, blank=False,
                            on_delete=models.CASCADE)

    active_hours_start = models.TimeField(auto_now_add=True, blank=True)

    active_hours_end = models.TimeField(auto_now_add=True, blank=True)

    message_limit = models.IntegerField(default=0)

    consecutive_hours = models.IntegerField(default=0)

    email_addr_list = models.TextField(
        default="{\"items\":[]}", blank=True, help_text='Email ID of the user to whom the mail sent on Analytics goes below set limit')

    class Meta:
        verbose_name = 'AnalyticsMonitoring'
        verbose_name_plural = 'AnalyticsMonitoring'

    def __str__(self):
        return self.bot.name


class ImageData(models.Model):

    image_path = models.TextField(help_text='Image url to store image data')

    left = models.IntegerField(default=0)

    right = models.IntegerField(default=0)

    width = models.IntegerField(default=32)

    height = models.IntegerField(default=20)

    class Meta:
        verbose_name = 'ImageData'
        verbose_name_plural = 'ImageData'

    def __str__(self):
        return self.image_path


class ApiIntegrationDetail(models.Model):
    tree = models.ForeignKey(
        Tree, null=False, blank=False, on_delete=models.CASCADE)

    url_access_token = models.TextField(default="", blank=True)

    header_access_token = models.TextField(default="", blank=True)

    url = models.TextField(default="", blank=True)

    header = models.TextField(default="", blank=True)

    request_packet = models.TextField(default="{ }", blank=True)

    response_packet = models.TextField(default="{ }", blank=True)

    error_response_packet = models.TextField(default="{ }", blank=True)

    basic_authorization_username = models.TextField(default="", blank=True)

    basic_authorization_password = models.TextField(default="", blank=True)

    bot_response_variable = models.TextField(default="", blank=True)

    bot_response_value = models.TextField(default="", blank=True)

    bot_error_response_value = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = 'ApiIntegrationDetail'
        verbose_name_plural = 'ApiIntegrationDetail'


class FlowAnalytics(models.Model):
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, help_text="User in the flow")

    intent_indentifed = models.ForeignKey(
        Intent, null=False, on_delete=models.CASCADE)

    previous_tree = models.ForeignKey(
        Tree, null=False, related_name="previous_tree_flow_analytics", on_delete=models.CASCADE)

    current_tree = models.ForeignKey(Tree, null=True, on_delete=models.CASCADE)

    user_message = models.CharField(default="", max_length=5000, blank=True)

    flow_analytics_variable = models.IntegerField(default=0, blank=True)

    created_time = models.DateTimeField(default=timezone.now)

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE)

    is_last_tree_child = models.BooleanField(
        default=False, help_text="Check if it's the last tree")

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL)

    is_flow_aborted = models.BooleanField(
        default=False, help_text='Designates whether the flow is aborted')

    class Meta:
        verbose_name = "FlowAnalytics"
        verbose_name_plural = "FlowAnalytics"

    def __str__(self):
        return self.intent_indentifed.name

    def save(self, *args, **kwargs):
        try:
            self.is_last_tree_child = self.current_tree.is_last_tree
            self.channel = self.user.channel
            self.category = self.intent_indentifed.category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in Save Flow Analytics %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

        super(FlowAnalytics, self).save(*args, **kwargs)


class DailyFlowAnalytics(models.Model):
    intent_indentifed = models.ForeignKey(
        Intent, null=False, on_delete=models.CASCADE, help_text="Intent identified ")

    previous_tree = models.ForeignKey(
        Tree, null=False, on_delete=models.CASCADE, related_name="previous_tree_daily_flow_analytics")

    current_tree = models.ForeignKey(
        Tree, null=True, on_delete=models.CASCADE, related_name="current_tree_daily_flow_analytics")

    created_time = models.DateTimeField(default=timezone.now, help_text="Date")

    count = models.IntegerField(default=0, blank=True)

    total_sum = models.IntegerField(default=0, blank=True, null=True)

    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="current_channel_daily_flow_analytics")

    is_last_tree_child = models.BooleanField(
        default=False, help_text="Check if it's the last tree Daily Flow")

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL)

    abort_count = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name = "DailyFlowAnalytics"
        verbose_name_plural = "DailyFlowAnalytics"

    def __str__(self):
        return self.previous_tree.name

    def save(self, *args, **kwargs):
        try:
            self.is_last_tree_child = self.current_tree.is_last_tree
            self.category = self.intent_indentifed.category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in Save Flow Analytics %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        super(DailyFlowAnalytics, self).save(*args, **kwargs)


class UserSession(models.Model):
    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)

    session_key = models.CharField(
        max_length=500, help_text="Django Session PK for perticular user")

    last_update_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + " - " + self.session_key + " - " + str(self.last_update_datetime)

    class Meta:
        verbose_name = 'UserSession'
        verbose_name_plural = 'UserSession'


class CommonUtilsFile(models.Model):
    code = models.TextField(
        default="", help_text="Write Common Utils Functions")
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)
    last_opened = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.bot.name) + "- CommonUtils - " + str(self.bot.pk)

    class Meta:
        verbose_name = 'CommonUtils'
        verbose_name_plural = 'CommonUtils'


@receiver(post_save, sender=CommonUtilsFile)
def set_common_utils_file_cache(sender, instance, **kwargs):
    bot_id = str(instance.bot.pk)
    common_utils_code = instance.code
    if not common_utils_code:
        common_utils_code = ""
    cache.set("CommonUtilsFileCode-" + bot_id, common_utils_code, settings.CACHE_TIME)


class TrafficSources(models.Model):
    web_page = models.TextField(default="", help_text="Website visited")
    bot_clicked_count = models.IntegerField(
        default=0, help_text="Number of times bot was clicked")
    web_page_visited = models.IntegerField(
        default=0, help_text="Number of times website was visited")
    visiting_date = models.DateField(default=timezone.now)
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)
    web_page_source = models.TextField(
        default="", null=True, blank=True, help_text="Source from where web_page was redirected")

    def __str__(self):
        return self.web_page

    class Meta:
        verbose_name = 'TrafficSources'
        verbose_name_plural = 'TrafficSources'


class WelcomeBannerClicks(models.Model):
    user_id = models.ManyToManyField(
        Profile, blank=True, help_text="Many to many field profile objects")
    web_page_visited = models.TextField(
        default="-", help_text="Website visited")
    visiting_date = models.DateField(default=timezone.now)
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)
    preview_source = models.TextField(
        default="", null=True, blank=True, help_text="Source image preview.")
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, null=True,
                               blank=True, help_text="Intent to be triggered if any.")

    def __str__(self):
        return str(self.preview_source)

    class Meta:
        verbose_name = 'WelcomeBannerClicks'
        verbose_name_plural = 'WelcomeBannerClicks'


class EasyChatAppFileAccessManagement(models.Model):

    bot = models.ForeignKey(
        'Bot', blank=True, null=True, default=None, on_delete=models.SET_NULL, help_text="Foreign key to the bot under which file is downloaded.")

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique access token key')

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    is_public = models.BooleanField(default=False)

    is_expired = models.BooleanField(default=False)

    is_authentication_required = models.BooleanField(default=False)

    is_customer_attachment = models.BooleanField(
        default=False, help_text="designates wheter the file is customer attachment or not")

    is_analytics_file = models.BooleanField(
        default=False, help_text="Designates whether the file is EasyChat Analytics File")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when access management object is created')

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.is_public)

    class Meta:
        verbose_name = 'EasyChatAppFileAccessManagement'
        verbose_name_plural = 'EasyChatAppFileAccessManagement'

    def is_obj_time_limit_exceeded(self):
        try:
            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)

            created_datetime = self.created_datetime.astimezone(
                tz)
            current_datetime = timezone.now().astimezone(tz)

            if (current_datetime - created_datetime).total_seconds() >= FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT * 60 * 60:
                return True

            return False
        except Exception:
            logger.warning("is_obj_time_limit_exceeded ", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return True


class SelfSignupUser(models.Model):

    firstname = models.TextField(default="", help_text="First Name")

    lastname = models.TextField(default="", help_text="Last Name")

    email_id = models.TextField(default="", help_text="Email Id")

    is_completed = models.BooleanField(default=False)

    token = models.UUIDField(
        help_text='unique access token key', default=uuid.uuid4)

    timestamp_user_creation = models.DateTimeField(default=timezone.now)

    total_attempts = models.IntegerField(default=0)

    def __str__(self):
        return str(self.email_id)

    class Meta:
        verbose_name = 'SelfSignupUser'
        verbose_name_plural = 'SelfSignupUsers'


class TelegramDetails(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    telegram_url = models.TextField(
        default="https://api.telegram.org/", blank=True, help_text="Telegram urls")

    telegram_api_token = models.TextField(
        default="", blank=True, help_text="Last Name")

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'TelegramDetails'
        verbose_name_plural = 'TelegramDetails'


class ViberDetails(models.Model):
    bot = models.ForeignKey(
        'EasyChatApp.Bot', null=True, blank=True, on_delete=models.SET_NULL, help_text="Foreign Key of bot to ViberDetails")

    viber_api_token = models.TextField(
        default="", blank=True, help_text="Viber Token")

    viber_bot_logo = models.TextField(
        default="{\"sender_logo\":[]}", help_text="ViberBot Sender Logo.")

    is_active = models.BooleanField(
        default=False, help_text="Active Status of ViberBot")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'ViberDetails'
        verbose_name_plural = 'ViberDetails'


class GMBDetails(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    gmb_agent_id = models.TextField(
        default="", blank=True, help_text="agent id of gmb agent ")

    gmb_brand_id = models.TextField(
        default="", blank=True, help_text="brand id of gmb to which agent belongs ")

    is_active = models.BooleanField(default=False)

    bot_display_name = models.TextField(
        default="CognoAI Agent", blank=True, help_text="bot message name for gmb agent")

    bot_display_image_url = models.TextField(
        default="https://storage.googleapis.com/sample-avatars-for-bm/bot-avatar.jpg", blank=True, help_text="bot message image for gbm agent")  # assuming https://storage.googleapis.com  has been whitlisted for on premise servers

    gmb_credentials_file_path = models.TextField(default="",
                                                 blank=True, null=True, help_text="file path of the api credentials file")

    gmb_privacy_policy_url = models.TextField(default="https://support.google.com/business/answer/3038177",
                                              blank=True, null=True, help_text="privacy policy url of the client ")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'GMBDetail'
        verbose_name_plural = 'GMBDetails'


class ViberMessageDetails(models.Model):
    message_id = models.TextField(
        default="", blank=True, help_text="message id received from viber message ")

    def __str__(self):
        return str(self.message_id)

    class Meta:
        verbose_name = 'ViberDetail'
        verbose_name_plural = 'ViberDetails'


class GMBMessageDetails(models.Model):

    message_id = models.TextField(
        default="", blank=True, help_text="message id received from gbm message ")

    def __str__(self):
        return str(self.message_id)

    class Meta:
        verbose_name = 'GMBDetail'
        verbose_name_plural = 'GMBDetails'


class MessageAnalyticsDaily(models.Model):
    total_messages_count = models.IntegerField(
        default=0, help_text="Total messages that day")
    answered_query_count = models.IntegerField(
        default=0, help_text="Answered queries that day")
    unanswered_query_count = models.IntegerField(
        default=0, help_text="Unanswered queries that day")
    intuitive_query_count = models.IntegerField(
        default=0, help_text="intuitive queries that day")
    total_message_count_mobile = models.IntegerField(
        default=0, help_text="Total messages that day from mobile")

    answered_query_count_mobile = models.IntegerField(
        default=0, help_text="Answered queries that day from mobile")
    intuitive_query_count_mobile = models.IntegerField(
        default=0, help_text="intuitive queries that day from mobile")
    
    unanswered_query_count_mobile = models.IntegerField(
        default=0, help_text="Unanswered queries that day from mobile")

    date_message_analytics = models.DateField(default=now, db_index=True)
    channel_message = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)
    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.date_message_analytics)

    class Meta:
        verbose_name = 'MessageAnalyticsDaily'
        verbose_name_plural = 'MessageAnalyticsDaily'


class WordCloudAnalyticsDaily(models.Model):
    word_cloud_dictionary = models.TextField(
        default="[]", help_text="Word Cloud Data")
    date = models.DateField(default=now, db_index=True)
    channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)
    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = 'WordCloudAnalyticsDaily'
        verbose_name_plural = 'WordCloudAnalyticsDaily'


class UnAnsweredQueries(models.Model):
    unanswered_message = models.TextField(
        default="", help_text="Word Cloud Data")
    channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)
    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)
    count = models.IntegerField(db_index=True,
                                default=0, help_text="UnAnswered query that day")
    date = models.DateField(default=now, db_index=True)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.unanswered_message)

    class Meta:
        verbose_name = 'UnAnsweredQueries'
        verbose_name_plural = 'UnAnsweredQueries'


class IntuitiveQuestions(models.Model):
    intuitive_message_query = models.TextField(
        default="", help_text="User Query")

    suggested_intents = models.ManyToManyField(
        "EasyChatApp.Intent", help_text="IntuitiveQuestions Intent many to many field")

    channel = models.TextField(default="", help_text="Channel Name")
    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)
    intuitive_message_query_hash = models.CharField(
        max_length=5000, default="", db_index=True, blank=True, null=True, help_text="Hashed value of intuitive questions")

    count = models.IntegerField(
        default=0, help_text="Intuitive questions count that day")

    date = models.DateField(default=now, db_index=True)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.intuitive_message_query) + "-" + str(self.date)

    class Meta:
        verbose_name = 'IntuitiveQuestions'
        verbose_name_plural = 'IntuitiveQuestions'


class UniqueUsers(models.Model):
    count = models.IntegerField(default=0, help_text="Count of users that day")

    users_count_mobile = models.IntegerField(default=0, help_text="Count of users that day with source as mobile")

    session_count = models.IntegerField(
        default=0, help_text="Count of total no of sessions of that day")

    business_initiated_session_count = models.IntegerField(
        default=0, help_text="Count of business initiated sessions of that day")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)

    date = models.DateField(default=now, db_index=True)

    channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)

    selected_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = 'UniqueUsers'
        verbose_name_plural = 'UniqueUsers'


class FormWidgetDataCollection(models.Model):
    form_name = models.CharField(
        max_length=5000, null=False, blank=False, help_text='Form widget name')
    form_data = models.CharField(
        max_length=5000, null=False, blank=False, help_text='Form widget name')
    date = models.DateTimeField(default=timezone.now)
    user_id = models.ForeignKey(
        'EasyChatApp.Profile', null=True, blank=True, on_delete=models.CASCADE)
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.CASCADE)
    intent = models.ForeignKey(
        'EasyChatApp.Intent', null=True, blank=True, on_delete=models.CASCADE)
    intent_name = models.CharField(
        max_length=5000, blank=True, help_text='Intent name')

    def __str__(self):
        return str(self.form_name)

    def save(self, *args, **kwargs):
        if self.intent:
            self.intent_name = self.intent.name
        super(FormWidgetDataCollection, self).save(*args, **kwargs)

    def get_datetime(self):
        try:
            import pytz
            est = pytz.timezone(settings.TIME_ZONE)
            return self.date.astimezone(est).strftime("%d %b %Y %I:%M %p")
        except Exception:
            return self.date.strftime("%d %b %Y %I:%M %p")

    class Meta:
        verbose_name = 'FormWidgetDataCollection'
        verbose_name_plural = 'FormWidgetDataCollection'


class AnalyticsExportRequest(models.Model):
    analytics_type = models.CharField(
        max_length=100, null=True, blank=True, choices=ANALYTICS_EXPORT_CHOICES, default="combined_global_export", help_text="Type of analytics data requested by user")
    request_datadump = models.TextField(
        default="{}", null=True, blank=True, help_text="Dump of the request data which has details like filter type, channel, etc.")
    request_time = models.DateTimeField(default=timezone.now)
    email_id = models.TextField(
        default="", null=False, blank=False, help_text='Email address to send analytics')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        'EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE)
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL)
    is_processing = models.BooleanField(default=False, null=False, blank=False, help_text="Designates whether this request is currently being processed or not")
    is_completed = models.BooleanField(default=False, null=False, blank=False)

    is_large_date_range_data = models.BooleanField(
        default=False, null=False, blank=False, help_text="If date interval is greater than 30 days then that request will be processed at night by cronjob")

    export_file_path = models.CharField(
        max_length=500, null=True, blank=True, help_text='Export file path generated by this request')

    time_taken = models.FloatField(
        default=0, null=True, blank=True, help_text="Time taken for processing this request (in seconds)")

    def __str__(self):
        if self.analytics_type and self.bot:
            return self.analytics_type + " - " + self.bot.name + " - " + self.email_id
        else:
            return "AnalyticsExportRequest - " + self.email_id

    class Meta:
        verbose_name = 'AnalyticsExportRequest'
        verbose_name_plural = 'AnalyticsExportRequest'


class AutomatedTestProgress(models.Model):
    user = models.ForeignKey(
        'EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE)
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL)
    test_cases_processed = models.IntegerField(
        default=0, help_text='Number of test cases processed in automated testing')
    one_test_process_time = models.FloatField(
        default=0.0, help_text='Time taken to process one test case')
    test_cases_passed = models.IntegerField(
        default=0, help_text="Number of test cases passed")
    is_automated_testing_completed = models.BooleanField(
        default=False, help_text='Indicates whether automated testing is completed')
    is_excel_created = models.BooleanField(
        default=False, help_text='Indicates whether excel is created after running automated test')

    is_testing_stopped_in_between = models.BooleanField(
        default=False, help_text='Indicates whether automated testing is stoped in between or not')

    last_tested_on = models.DateTimeField(
        default=timezone.now, help_text="Date time when the bot was tested for the last time")

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name = 'AutomatedTestProgress'
        verbose_name_plural = 'AutomatedTestProgress'


class AutomatedTestResult(models.Model):

    automated_test_progress_obj = models.ForeignKey(
        AutomatedTestProgress, null=True, blank=True, on_delete=models.CASCADE)

    original_intent = models.ForeignKey(
        Intent, related_name="original_intent", null=True, blank=True, on_delete=models.CASCADE)

    identified_intents = models.ManyToManyField(
        Intent, related_name="identified_intent", blank=True)

    query_sentence = models.CharField(
        max_length=500, default="", blank=True, null=True, help_text="query sentence for which it is tested")

    status = models.CharField(max_length=10, default="Pass", blank=True,
                              null=True, help_text="Status wheter testcase passed or failed")

    cause = models.CharField(max_length=500, default="Valid intent identified.",
                             blank=True, null=True, help_text="Cause for the current status")

    is_processed = models.BooleanField(
        default=False, help_text='Indicates whether this object is processed or not')

    def __str__(self):
        return str(self.original_intent.name) + " - " + str(self.status)

    def get_identified_intent_name_list(self):
        intent_name_list = []

        for intent in self.identified_intents.all():
            intent_name_list.append(intent.name)

        return intent_name_list

    def get_identified_intent_pk_list(self):
        intent_pk_list = []

        for intent in self.identified_intents.all():
            intent_pk_list.append(intent.pk)

        return intent_pk_list

    class Meta:
        verbose_name = 'AutomatedTestResult'
        verbose_name_plural = 'AutomatedTestResult'


class ChunksOfSuggestions(models.Model):
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL)
    suggestion_list = models.TextField(
        default="[]", help_text="Suggestion list of all intents.")

    class Meta:
        verbose_name = 'ChunksOfSuggestions'
        verbose_name_plural = 'ChunksOfSuggestions'


class EasyChatPIIDataToggle(models.Model):
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, blank=False)
    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=False, blank=False)
    otp = models.CharField(max_length=200)
    token = models.UUIDField(default=uuid.uuid4,
                             editable=False)
    is_expired = models.BooleanField(default=True, null=False, blank=False)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name = 'EasyChatPIIDataToggle'
        verbose_name_plural = 'EasyChatPIIDataToggle'


class EasyChatOTPDetails(models.Model):

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, blank=False)

    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=True, blank=True)

    email_id = models.TextField(
        default="", blank=True, null=True, help_text="email id on which otp is sent")

    otp = models.CharField(max_length=200)

    is_expired = models.BooleanField(default=True, null=False, blank=False)

    otp_sent_on = models.DateTimeField(
        default=timezone.now, help_text="Date time when the otp is sent")

    token = models.UUIDField(
        help_text='unique access token key', default=uuid.uuid4)

    def __str__(self):
        return str(self.user.username) + " - " + str(self.email_id)

    class Meta:
        verbose_name = 'EasyChatOTPDetails'
        verbose_name_plural = 'EasyChatOTPDetails'


class CSATFeedBackDetails(models.Model):
    number_of_feedbacks = models.IntegerField(
        default=0, blank=False, null=False)
    collect_phone_number = models.BooleanField(
        default=False, blank=False, null=False)
    collect_email_id = models.BooleanField(
        default=False, blank=False, null=False)
    mark_all_fields_mandatory = models.BooleanField(
        default=False, blank=False, null=False)
    all_feedbacks = models.CharField(
        default="[]", blank=True, null=True, max_length=500000)
    bot_obj = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return str(self.bot_obj.name)

    class Meta:
        verbose_name = 'CSATFeedBackDetails'
        verbose_name_plural = 'CSATFeedBackDetails'


class WhitelistedEnglishWords(models.Model):

    keywords = models.TextField(
        default="", help_text="These words will be considered as english words. Add words in lower case seperated by comma")

    bot_obj = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return "WhitelistedEnglishWords " + str(self.bot_obj.name)

    class Meta:
        verbose_name = 'WhitelistedEnglishWords'
        verbose_name_plural = 'WhitelistedEnglishWords'


class EasyChatSessionIDGenerator(models.Model):

    user = models.ForeignKey(
        'Profile', null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text='Foreign Key to Profile Object of this Session')

    token = models.UUIDField(
        primary_key=True, default=uuid.uuid4, help_text='unique easychat session id')

    session_start_date_time = models.DateTimeField(
        default=timezone.now, help_text='datetime of when the session was started')

    is_expired = models.BooleanField(
        default=False, help_text='Designates whether the session is expired or not.')

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'EasyChatSessionIDGenerator'
        verbose_name_plural = 'EasyChatSessionIDGenerator'

    def is_session_expired(self):
        try:

            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            session_date = self.session_start_date_time.astimezone(
                tz)
            session_date = session_date.date()
            current_date = timezone.now().astimezone(tz).date()

            if session_date != current_date:
                self.is_expired = True
                self.save(update_fields=['is_expired'])
                return True

            return False
        except Exception:
            logger.warning("EasyChatSessionIDGenerator ", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            self.is_expired = True
            self.save(update_fields=['is_expired'])
            return True


"""
this model is for mapping user id for with easychatsessionidgenrator object  this can be usefull for maintaing session in channels which have fixed userid for a particular user like whatsapp
"""


class WhatsAppUserSessionMapper(models.Model):

    user_id = models.CharField(
        max_length=100, db_index=True, help_text="Unique user id.")

    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=True, blank=True)

    session_obj = models.ForeignKey(EasyChatSessionIDGenerator, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    is_session_started = models.BooleanField(
        default=True, help_text="Weather the session is started or not")
    
    is_business_initiated_session = models.BooleanField(
        default=False, help_text="Designates whether the chat was initiated by business end")

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'WhatsAppUserSessionMapper'
        verbose_name_plural = 'WhatsAppUserSessionMapper'

    def is_current_session_obj_is_longer_than_tweenty_four_hours(self):
        try:

            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            session_datetime = self.session_obj.session_start_date_time.astimezone(
                tz)

            current_datetime = timezone.now().astimezone(tz)

            if (current_datetime - session_datetime).total_seconds() >= 24 * 60 * 60:
                return True

            return False
        except Exception:
            logger.warning("EasyChatSessionIDGenerator ", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return True


class PasswordHistory(models.Model):
    user = models.ForeignKey(User, null=True, blank=True,
                             on_delete=models.SET_NULL)

    password = models.CharField(max_length=256,
                                null=True,
                                blank=True,
                                help_text='Old Password')

    request_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime of request for password change')

    def save(self, *args, **kwargs):
        self.password = hashlib.sha256(self.password.encode()).hexdigest()
        super(PasswordHistory, self).save(*args, **kwargs)


class RequiredBotTemplate(models.Model):
    bot = models.ForeignKey('Bot', null=True, blank=True,
                            on_delete=models.CASCADE)
    language = models.ForeignKey(Language, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    placeholder = models.CharField(max_length=256,
                                   default="Type here...",
                                   help_text='Placeholder text')
    close_button_tooltip = models.CharField(max_length=256,
                                            default="Close",
                                            help_text='Close button text')

    minimize_button_tooltip = models.CharField(max_length=256,
                                               default="Minimize",
                                               help_text='Minimize button text')

    home_button_tooltip = models.CharField(max_length=256,
                                           default="Home",
                                           help_text='Home button text')
    mic_button_tooltip = models.CharField(max_length=256,
                                          default="Microphone",
                                          help_text='mic text')

    typing_text = models.CharField(max_length=256,
                                   default="Typing",
                                   help_text='Typing loader text')

    send_text = models.CharField(max_length=256,
                                 default="Send",
                                 help_text='Send button text')

    cards_text = models.CharField(max_length=256,
                                  default="Know more",
                                  help_text='know more in cards text')

    go_back_text = models.CharField(max_length=256,
                                    default="Go Back",
                                    help_text='Go back text')

    back_text = models.CharField(max_length=256,
                                 default="Back",
                                 help_text='Back text')

    menu_text = models.CharField(max_length=256,
                                 default="Menu",
                                 help_text='Menu text')

    minimize_text = models.CharField(max_length=256,
                                     default="Click here to minimize.",
                                     help_text='tooltipped text to minimize bot icon.')

    maximize_text = models.CharField(max_length=256,
                                     default="Click here to maximize.",
                                     help_text='tooltipped text to maximize bot icon.')

    dropdown_text = models.CharField(max_length=256,
                                     default="Select one of the following.",
                                     help_text='dropdown text')

    search_text = models.CharField(max_length=256,
                                   default="Search",
                                   help_text='search text')

    start_text = models.CharField(max_length=256,
                                  default="Start",
                                  help_text='Start text')

    stop_text = models.CharField(max_length=256,
                                 default="Stop",
                                 help_text='Stop text')

    submit_text = models.CharField(max_length=256,
                                   default="Submit$$$Confirm",
                                   help_text='Submit text')

    uploading_video_text = models.CharField(max_length=256,
                                            default="Your video is uploaded successfully",
                                            help_text='video uploading success text after video recording')

    cancel_text = models.CharField(max_length=256,
                                   default="Cancel",
                                   help_text='Cancel text')

    file_attachment_text = models.CharField(max_length=256,
                                            default="Drag and drop your files here<br>Or Click in this area.",
                                            help_text='Drag and drop your files here<br>Or Click in this area text')

    file_size_limit_text = models.CharField(max_length=256,
                                            default="File size must be less than",
                                            help_text='File size must be less than  MB, text')

    file_upload_success_text = models.CharField(max_length=256,
                                                default="Your file has been uploaded successfully.",
                                                help_text='Text after uploading file through attachment widget')

    feedback_text = models.CharField(max_length=256,
                                     default="Please provide your feedback",
                                     help_text='Text for requesting user to provide feedback')

    positive_feedback_options_text = models.TextField(default="Easy Communication$$$Fully Satisfied$$$Quick Response$$$Query Resolved Quickly$$$Good Experience",
                                                      help_text='Text after uploading file through attachment widget')

    negative_feedback_options_text = models.TextField(default="Inappropriate Answer$$$Response is slow$$$Need more information$$$I couldn’t find what I was looking for$$$Content is too complicated",
                                                      help_text='Text after uploading file through attachment widget')

    feedback_error_text = models.CharField(max_length=500,
                                           default="Please select from the below options.",
                                           help_text='Text shown, when user click on submit without selecting any point.')

    success_feedback_text = models.CharField(max_length=500,
                                             default="Thank you for your feedback",
                                             help_text='Text shown, after submitting feedback.')

    csat_form_text = models.TextField(default="Was I Helpful?$$$Your feedback matters!$$$We value your feedback$$$Please complete this form to improve the experience.$$$Type here if selected others$$$Please provide your details so that we can contact you:$$$Enter Phone Number$$$Enter Email id$$$Tell us about your experience",
                                      help_text='All text of CSAT form in order.')

    csat_form_error_mobile_email_text = models.TextField(default="Select at least one feedback.$$$Please enter a valid phone number.$$$Please fill a valid email id.",
                                                         help_text='All text of CSAT form in order.')

    csat_emoji_text = models.TextField(
        default="Angry$$$Sad$$$Neutral$$$Happy$$$Very Happy", help_text='All emoji text of CSAT.')

    date_range_picker_text = models.TextField(default="From Date$$$To Date$$$From Time$$$To Time$$$Select Range$$$Date$$$Time$$$Min$$$Max$$$Range$$$Select Value$$$Selected Value",
                                              help_text='All text for date, time and range slider.')

    general_text = models.TextField(default="Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not answer your query for now. Please try again after some time.$$$Read More$$$Read Less$$$Show Less$$$View more$$$speak now$$$This content is blocked. Please contact the site owner to fix the issue.",
                                    help_text='All text for date, time and range slider.')

    form_widget_text = models.TextField(default="Please fill the form$$$Are you sure you want to submit these details?$$$Yes$$$No",
                                        help_text='Text for form widget.')

    choose_language = models.CharField(
        max_length=256, default="Choose Language$$$Disclaimer", help_text='Text for choosing language')

    mute_tooltip_text = models.CharField(
        max_length=256, default="Mute", help_text='Tooltip text for mute icon')

    unmute_tooltip_text = models.CharField(
        max_length=256, default="UnMute", help_text='Tooltip text for unmute icon')

    no_result_found_text = models.CharField(
        max_length=256, default="No results found", help_text='No result found in dropdown')

    form_widget_error_text = models.TextField(
        default="Please enter a valid 6 digit OTP.$$$Please enter a valid 4 digit OTP.$$$Please enter a valid Email Id.$$$Invalid PAN number$$$Please enter a valid name.$$$Save$$$Reset$$$Mobile number is invalid. Please try again.", help_text="Form widget validator error text")

    widgets_response_text = models.TextField(
        default="File has been uploaded successfully$$$Date$$$Time$$$Add$$$From$$$To", help_text="Widgets response texts")

    greeting_and_welcome_text = models.TextField(
        default="Hello$$$Welcome to", help_text="greeting text and welcome text for theme 3")

    end_chat = models.CharField(
        max_length=256, default="Do you want to resume the chat later or end the chat?$$$Resume Later$$$End Chat", help_text='End chat text for android dialog')

    auto_language_detection_text = models.TextField(
        default="Do you want to change your language to {}?$$$The language detected in the query is {} is not available in the Bot. Available language in the Bot are: ", help_text="Text for Bot Auto Language detection")

    livechat_form_text = models.TextField(
        default="Connect with Agent$$$Please fill in these details to connect to our agent$$$Enter your Name$$$Enter Email-ID$$$Enter Phone Number$$$Continue$$$To connect with LiveChat Agent, please Click \"Continue\" and submit your details or Click \"Back\" to end the conversation.$$$Choose Category$$$Please select a valid category.$$$Unable to raise request, try once again. Please make sure you are not in an authenticated window.",
        help_text='All text of LiveChat form in order.')

    livechat_system_notifications = models.TextField(
        default="Your request is in process$$$has joined the chat. Please ask your queries now.$$$Looks like your internet is weak. Unable to connect.$$$Our chat representatives are unavailable right now. Please try again in some time.$$$Your chat has ended$$$Agent has left the session. LiveChat session ended.$$$Thank you for connecting with us. Hoping to help you in the future again.$$$End Chat",
        help_text='All text of LiveChat system notifications.')
    
    livechat_system_notifications_ios = models.TextField(
        default="To avoid disconnecting with the agent, please don't minimize the browser during interaction$$$Your Internet connection was weak (or you minimised the app). Chat is disconnected",
        help_text='All text of LiveChat system notifications for ios device.')

    livechat_voicecall_notifications = models.TextField(
        default="Voice Call Request has been sent$$$Voice Call Started$$$Voice Call Ended$$$Request Successfully Sent",
        help_text='All text of LiveChat voice call notifications')

    livechat_vc_notifications = models.TextField(
        default="Video Call Request has been sent$$$Video Call Started$$$Video Call Ended$$$Please join the following link for video call$$$Agent has accepted the request. Please join the following link$$$Join Now$$$Voice Call$$$Video Call$$$Agent has initiated a voice call. Would you like to connect?$$$Agent has initiated a video call. Would you like to connect?$$$Agent Cancelled the Meet.$$$Request Successfully Sent$$$Please end the ongoing call.$$$has accepted the voice call request$$$has rejected the voice call request$$$Reject$$$Accept$$$Connect$$$OK$$$Resend$$$Agent has accepted the Video Call request.$$$has rejected the video call request",
        help_text='All text of LiveChat video call notifications')
    
    livechat_transcript_text = models.TextField(
        default="Goodbye, Hope I was able to help you!$$$If you want a transcript of the chat above on your mail$$$CLICK HERE$$$To get your conversation on mail$$$The transcript will be sent over mail$$$Click on check box to get chat transcript on your mail",
        help_text='All text of LiveChat transcript')

    livechat_feedback_text = models.TextField(
        default="Feedback$$$On a scale of 0-10, how likely are you to recommend LiveChat to a friend or colleague?$$$No, Thanks$$$Comments (optional)$$$Remarks$$$Submit$$$Your video call has been ended.",
        help_text='All text of LiveChat feedback form in order.')
    
    livechat_validation_text = models.TextField(
        default="Malicious File not accepted$$$File type not supported. Please try again with supported file (_ etc)$$$File size is large. Please try again with file size less than 5 MB",
        help_text='All text of LiveChat validations')

    attachment_tooltip_text = models.CharField(
        max_length=256, default="Attachment$$$Please upload/delete the previous attachment.$$$Upload", help_text='Tooltip text for attachment icon')

    powered_by_text = models.TextField(
        default="Powered by", help_text="Powered by text")

    livechat_cb_notifications = models.TextField(
        default="Cobrowsing Session$$$Cobrowsing Session Started$$$Cobrowsing Session Ended$$$Please end the ongoing Cobrowsing Session.",
        help_text='All text of LiveChat Cobrowsing notifications')

    do_not_disturb_text = models.TextField(
        default="Do not disturb$$$Are you sure, you want to enable Do not disturb? By clicking Yes, form assistant will be disabled.$$$Great, How may I help you?", help_text="Do not disturb text")

    pdf_view_document_text = models.TextField(
        default="View Document", help_text="PDF View Document text")

    phone_number_too_long_text = models.TextField(
        default="The entered number is too long", help_text="Phone widget error message for long number")

    phone_number_too_short_text = models.TextField(
        default="The entered number is too short", help_text="Phone widget error message for short number")

    invalid_number_text = models.TextField(
        default="Please enter a valid number", help_text="Phone widget error message for invalid number")

    invalid_country_code = models.TextField(
        default="Invalid country code", help_text="Phone widget error message for invalid country code")

    bot_name = models.CharField(
        max_length=90, help_text="Template Bot Name", null=True, blank=True)

    frequently_asked_questions_text = models.TextField(
        default="Frequently asked questions$$$Questions customer ask oftenly$$$Search here$$$View All$$$Was it helpful?$$$Skip$$$Ask your query", help_text="Frequently Asked Questions text")

    chat_with_text = models.CharField(
        max_length=256, default="Chat with", help_text='Bot header text beside name')
    
    query_api_failure_text = models.TextField(
        default="We are unable to process your request at this time. Please try again later.", help_text='Message displayed to user when Query API fails')

    widgets_placeholder_text = models.TextField(default="Choose from the above options$$$Attach a file to submit$$$Provide a number above$$$Select a value above$$$Record a video to send$$$Choose a date and time above$$$Fill the form and submit", help_text="This designates placeholder that will be displayed in the chatbot when any widget response appears.")

    range_slider_error_messages = models.TextField(default="Please select a valid value in given range$$$Please select a valid value in given range$$$Please enter a valid input$$$Please enter a valid minimum value$$$Please enter a valid maximum value$$$Mimimum value cannot be less than given range$$$Minimum value cannot be greater than given range$$$Maximum value cannot be greater than given range$$$Maximum value cannot be lesser than given range$$$Minimum value cannot be greater than maximum value", help_text="These are the error messages that will be shown if user enters incorrect input.")

    # if you add any other text field here please also add the same in EasyChatApp/utils_bot.py >
    # def get_language_constant_dict ,
    # def check_and_create_required_bot_language_template_for_selected_language
    # and def update_language_template_object

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'RequiredBotTemplate'
        verbose_name_plural = 'RequiredBotTemplate'

    def get_did_you_mean_text(self):
        try:
            return self.general_text.split("$$$")[0]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_internal_server_error_text(self):
        try:
            return self.general_text.split("$$$")[1]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_invalid_bot_text(self):
        try:
            return self.general_text.split("$$$")[2]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_invalid_channel_text(self):
        try:
            return self.general_text.split("$$$")[3]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_more_than_one_session_running_text(self):
        try:
            return self.general_text.split("$$$")[4]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_upset_text(self):
        try:
            return self.general_text.split("$$$")[5]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_negative_feedback_text(self):
        try:
            return self.general_text.split("$$$")[6]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_positive_feedback_text(self):
        try:
            return self.general_text.split("$$$")[7]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_feedback_text(self):
        try:
            return self.general_text.split("$$$")[8]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_easysearch_text(self):
        try:
            return self.general_text.split("$$$")[9]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_assist_text(self):
        try:
            return self.general_text.split("$$$")[10]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_invalid_session_id_text_response(self):
        try:
            return self.general_text.split("$$$")[11]
        except Exception:
            logger.warning("Date picker template issue", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_bot_auto_detected_language_supported_text(self):
        try:
            language_script_type = self.language.language_script_type
            auto_detect_language_text = f"<div style= 'direction:{language_script_type}'>" + self.auto_language_detection_text.split("$$$")[
                0] + "</div>"
            language_display_name = self.language.display
            language_name_in_english = self.language.name_in_english

            if self.language.lang != "en":
                auto_detect_language_text += "<div style= 'direction: ltr; padding-top: 5px;'> (Do you want to change your language to {}?) </div>".format(
                    language_name_in_english)

            return auto_detect_language_text.format(language_display_name)

        except Exception:
            logger.warning("get_bot_auto_detected_language_supported_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

            return "Do you want to change your language ?"

    def get_bot_auto_detected_language_not_supported_text(self, detected_language_name, list_of_languages):
        try:
            auto_detect_language_text = self.auto_language_detection_text.split("$$$")[
                1]

            final_text = auto_detect_language_text.format(
                detected_language_name)

            final_text = final_text + "<br> <ul>"

            for language in list_of_languages:
                single_lang = "<li> " + language + " </li>"
                final_text = final_text + single_lang

            final_text = final_text + "</ul>"

            return final_text

        except Exception:
            logger.warning("get_bot_auto_detected_language_not_supported_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_yes_and_no_text(self):

        try:
            form_widget_text = self.form_widget_text.split("$$$")

            return form_widget_text[2], form_widget_text[3]
        except Exception:
            logger.warning("get_yes_and_no_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return ""

    def get_confirm_text(self):
        try:
            confirm_text = self.submit_text.split("$$$")

            return confirm_text[1]
        except Exception:
            logger.warning("get_yes_and_no_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return "Confirm"

    def get_disclaimer_text(self):
        try:
            disclaimer_text = self.choose_language.split("$$$")

            return disclaimer_text[1]
        except Exception:
            logger.warning("get_yes_and_no_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return "Disclaimer"

    def get_cancel_text(self):
        try:
            return self.cancel_text

        except Exception:
            logger.warning("get_cancel_text", extra={
                           'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            return "Cancel"


class EasyChatTranslationCache(models.Model):
    input_text_hash_data = models.TextField(
        default="", db_index=True, help_text="md5 hash")

    output_text_hash_data = models.TextField(
        default="", db_index=True, help_text="md5 hash")

    input_text = models.TextField(default="", help_text="User's text")

    translated_data = models.TextField(
        default="", help_text="text after translation")

    lang = models.CharField(max_length=10, default="en",
                            null=True, help_text="Language")

    def __str__(self):
        return str(self.translated_data)

    class Meta:
        verbose_name = 'EasyChatTranslationCache'
        verbose_name_plural = 'EasyChatTranslationCache'


class EasyChatSpellCheckerWord(models.Model):
    word = models.CharField(default="", max_length=50, db_index=True,
                            help_text="Custom word which is not present in spell checker")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "EasyChatSpellCheckerWord"
        verbose_name_plural = "EasyChatSpellCheckerWords"

    def __str__(self):
        return self.word

# Lanaguage Tunning


class LanguageTuningChoicesTable(models.Model):
    language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.CASCADE, help_text="Intent language tunning table")

    choices = models.ForeignKey(
        Choice, null=True, blank=True, on_delete=models.CASCADE)

    display = models.TextField(default="", help_text="display of choices")

    value = models.TextField(default="", help_text="Value of choices")

    class Meta:
        verbose_name = "LanguageTuningChoicesTable"
        verbose_name_plural = "LanguageTuningChoicesTables"

    def __str__(self):
        return self.display


class LanguageTuningBotResponseTable(models.Model):
    language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.CASCADE, help_text="Intent language tunning table")

    bot_response = models.ForeignKey(
        BotResponse, null=True, blank=True, on_delete=models.CASCADE)

    sentence = models.TextField(
        default="{\"items\":[{\"text_response\":\"\", \"speech_response\":\"\", \"text_reprompt_response\":\"\", \"speech_reprompt_response\":\"\", \"tooltip_text\":\"\"}]}")

    choices = models.ManyToManyField(LanguageTuningChoicesTable, blank=True)

    cards = models.TextField(default="{\"items\":[]}", null=True, blank=True)

    table = models.TextField(default="{\"items\":[]}", null=True, blank=True)

    modes = models.TextField(default="{}")

    modes_param = models.TextField(default="{}")

    auto_response = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "LanguageTuningBotResponseTable"
        verbose_name_plural = "LanguageTuningBotResponseTables"

    def __str__(self):
        return str(self.sentence)


class LanguageTuningTreeTable(models.Model):
    language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.CASCADE, help_text="Tree language tunning table")

    tree = models.ForeignKey(
        Tree, null=True, blank=True, on_delete=models.CASCADE)

    response = models.ForeignKey(
        LanguageTuningBotResponseTable, null=True, blank=True, on_delete=models.CASCADE)

    multilingual_name = models.TextField(
        default="", help_text="Multilingual name")

    class Meta:
        verbose_name = "LanguageTuningTreeTable"
        verbose_name_plural = "LanguageTuningTreeTables"

    def __str__(self):
        return self.multilingual_name

    def get_response_without_html(self):
        try:
            if self.tree == None:
                return "No response"

            if self.tree.response == None:
                return "No response"

            if self.tree.response.sentence == None:
                return "No response"

            sentences = json.loads(self.response.sentence)["items"]
            text_response = sentences[0]["text_response"][:200]
            regex_cleaner = re.compile('<.*?>')
            cleaned_raw_str = re.sub(regex_cleaner, '', text_response)
            return cleaned_raw_str
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_response %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return "No response"

    def get_response(self):
        try:
            if self.tree == None:
                return "No response"

            if self.tree.response == None:
                return "No response"

            if self.tree.response.sentence == None:
                return "No response"

            sentences = json.loads(self.response.sentence)["items"]
            text_response = sentences[0]["text_response"]
            # text_response = text_response.replace("<p><br></p>", "<p></p>").replace(
            #     "</p><p>", "<br>").replace("</p>", "").replace("<p>", "")
            text_response = BeautifulSoup(text_response).text.strip()
            text_response = text_response[:200]
            return text_response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_response %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return "No response"


class LanguageTuningIntentTable(models.Model):
    language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.CASCADE, help_text="Intent language tunning table")

    intent = models.ForeignKey(
        Intent, null=True, blank=True, on_delete=models.CASCADE)

    tree = models.ForeignKey(
        LanguageTuningTreeTable, null=True, blank=True, on_delete=models.CASCADE, help_text="Tree language tunning table")

    multilingual_name = models.TextField(
        default="", help_text="Multilingual name")

    class Meta:
        verbose_name = "LanguageTuningIntentTable"
        verbose_name_plural = "LanguageTuningIntentTables"

    def __str__(self):
        return self.multilingual_name


class ExcelProcessingProgress(models.Model):
    is_processing_completed = models.BooleanField(
        default=False, help_text="Create faqs/flows using excel process is complete/incomplete")

    status = models.CharField(max_length=10, default="", null=True,
                              help_text="Create faqs/flows using excel process status")

    status_message = models.TextField(
        default="", null=True, blank=True, help_text="Success or error message of process.")

    class Meta:
        verbose_name = "ExcelProcessingProgress"
        verbose_name_plural = "ExcelProcessingProgress"

    def __str__(self):
        return str(self.pk)


class GBMSurveyDetails(models.Model):

    user_profile = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.SET_NULL)

    survey_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="unique id of the survey sent")

    survey_sent_on = models.DateTimeField(
        default=timezone.now, help_text="Date and time of survey was sent")

    class Meta:
        verbose_name = "GBMSurveyDetail"
        verbose_name_plural = "GBMSurveyDetails"

    def __str__(self):
        return str(self.user_profile) + "-" + str(self.survey_id)


class GBMSurveyQuestion(models.Model):

    question_id = models.CharField(max_length=100, null=False, blank=False,
                                   help_text='Question id for the GBM survey question')

    response_score_mapper = models.TextField(
        default="{}", null=True, blank=True, help_text='Map response with desired csat score like {"yes":5,"no":1}')

    class Meta:
        verbose_name = "GBMSurveyQuestion"
        verbose_name_plural = "GBMSurveyQuestions"

    def __str__(self):
        return str(self.question_id) + "-" + str(self.pk)


class GBMCSATMapping(models.Model):

    bot = models.ForeignKey('Bot', blank=True, null=True,
                            on_delete=models.CASCADE, help_text="Bot obj")

    questions = models.ManyToManyField(
        'EasyChatApp.GBMSurveyQuestion', blank=True, help_text='Questions for gbm')

    class Meta:
        verbose_name = "GBMCSATMapping"
        verbose_name_plural = "GBMCSATMappings"

    def __str__(self):
        return str(self.bot)


class EasyChatMailerAnalyticsProfile(models.Model):

    name = models.CharField(
        max_length=256, null=True, blank=True)

    bot = models.ForeignKey(
        'bot', null=True, blank=True, on_delete=models.SET_NULL)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mailer anlytics profile is created')

    last_updated_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mailer anlytics profile was last updated')

    email_frequency = models.TextField(
        default="['daily']", null=True, blank=True)

    email_address = models.TextField(default="[]", null=True, blank=True)

    email_subject = models.TextField(
        default=DEFAULT_MAIL_SUBJECT, null=True, blank=True)

    bot_accuracy_threshold = models.TextField(
        default="0", null=True, blank=True)

    is_table_enabled = models.BooleanField(default=True)

    table_parameters = models.ForeignKey(
        'EasyChatMailerTableParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_graph_enabled = models.BooleanField(default=False)

    graph_parameters = models.ForeignKey(
        'EasyChatMailerGraphParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_attachment_enabled = models.BooleanField(default=False)

    attachment_parameters = models.ForeignKey(
        'EasyChatMailerAttachmentParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'EasyChatMailerAnalyticsProfile'
        verbose_name_plural = 'EasyChatMailerAnalyticsProfile'


class EasyChatMailerGraphParameters(models.Model):

    profile = models.ForeignKey(
        'EasyChatMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    graph_parameters = models.TextField(default="[]", null=True, blank=True)

    message_analytics_graph = models.TextField(
        default="[]", null=True, blank=True)

    def __str__(self):
        profile_name = "Deleted Profile"
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'EasyChatMailerGraphParameters'
        verbose_name_plural = 'EasyChatMailerGraphParameters'


class EasyChatMailerTableParameters(models.Model):

    profile = models.ForeignKey(
        'EasyChatMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    count_variation = models.TextField(
        default="['daily']", null=True, blank=True)

    channels = models.TextField(default="[]", null=True, blank=True)

    message_analytics = models.TextField(default="[]", null=True, blank=True)

    session_analytics = models.TextField(default="[]", null=True, blank=True)

    user_analytics = models.TextField(default="[]", null=True, blank=True)

    flow_completion = models.TextField(default="", null=True, blank=True)

    intent_analytics = models.TextField(default="", null=True, blank=True)

    traffic_analytics = models.TextField(default="", null=True, blank=True)

    livechat_analytics = models.TextField(default="[]", null=True, blank=True)

    language_analytics = models.TextField(default="[]", null=True, blank=True)

    language_query_analytics = models.TextField(default="[]", null=True, blank=True)

    def __str__(self):
        profile_name = "Deleted Profile"
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'EasyChatMailerTableParameters'
        verbose_name_plural = 'EasyChatMailerTableParameters'


class EasyChatMailerAttachmentParameters(models.Model):

    profile = models.ForeignKey(
        'EasyChatMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    attachments = models.TextField(default="[]", null=True, blank=True)

    def __str__(self):
        profile_name = "Deleted Profile"
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'EasyChatMailerAttachmentParameters'
        verbose_name_plural = 'EasyChatMailerAttachmentParameters'


class EasyChatMailerAuditTrail(models.Model):

    profile = models.ForeignKey(
        'EasyChatMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    email_frequency = models.TextField(default="", null=True, blank=True)

    sent_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        profile_name = "Deleted Profile"
        if self.profile:
            profile_name = self.profile.name + \
                " - " + str(self.profile.bot.name)
        return profile_name

    class Meta:
        verbose_name = 'EasyChatMailerAuditTrail'
        verbose_name_plural = 'EasyChatMailerAuditTrail'


class EasyChatUserAuthenticationStatus(models.Model):
    user = models.ForeignKey(
        'Profile', null=True, blank=True, on_delete=models.SET_NULL)

    bot = models.ForeignKey(
        'bot', null=True, blank=True, on_delete=models.SET_NULL)

    channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, on_delete=models.SET_NULL,)

    is_authenticated = models.BooleanField(
        default=False, help_text='Designates whether user is authenticated or not')

    unique_token = models.CharField(max_length=500, null=True, blank=False,
                                    help_text="Unique parameters for user authentication, it may be mobile number, loand number, client id etc")

    auth_date = models.DateField(
        default=now, db_index=True, help_text="Date when user authentication was done")

    def __str__(self):
        profile_name = "Deleted Profile"
        try:
            if self.user:
                profile_name = self.user.user_id
        except Exception:
            profile_name = "Deleted Profile"

        return profile_name + ' - ' + str(self.is_authenticated)

    class Meta:
        verbose_name = 'EasyChatUserAuthenticationStatus'
        verbose_name_plural = 'EasyChatUserAuthenticationStatus'


class SignInProcessor(models.Model):

    name = models.CharField(default="", max_length=100,
                            help_text="API tree name")

    api_caller = models.TextField(default="def f():\n    return response")

    class Meta:
        verbose_name = "Sign In Processor"
        verbose_name_plural = "Sign In Processors"

    def __str__(self):
        return self.name

    def save(self, from_backend=False, *args, **kwargs):
        # from_backend: This is true if you are trying to create an object from
        # console, false otherwise.
        if from_backend:
            super(SignInProcessor, self).save(*args, **kwargs)
        else:
            try:
                api_tree_objs = SignInProcessor.objects.filter(name=self.name)
                if len(api_tree_objs) > 0:
                    raise ValidationError('This name already exists.')
            except Exception:
                logger.info("Matching processor name doesn't exists", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            super(SignInProcessor, self).save(*args, **kwargs)


class GoogleAlexaProjectDetails(models.Model):

    name = models.CharField(
        max_length=200, default="")

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE)

    project_id = models.CharField(
        max_length=200, default="", help_text="project id of google home")

    welcome_image_src = models.CharField(
        default="", max_length=2000, null=False, blank=False, help_text="welcome image file src")

    client_id = models.CharField(
        max_length=300, default="", help_text="client id")

    client_secret = models.CharField(
        max_length=300, default="", help_text="clientsecret")

    client_type = models.CharField(
        max_length=100, default="confidential", help_text="Client type ")

    authorization_grant_type = models.CharField(
        max_length=100, default="authorization-code", help_text="what type of authorization is thier")

    redirect_uris = models.CharField(
        max_length=400, default="", help_text="redirection url")

    get_otp_processor = models.ForeignKey(SignInProcessor, null=True, blank=True, related_name='get_otp_processor',
                                          on_delete=models.SET_NULL)

    verify_otp_processor = models.ForeignKey(SignInProcessor, null=True, blank=True, related_name='verify_otp_processor',
                                             on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'GoogleAlexaProjectDetails'
        verbose_name_plural = 'GoogleAlexaProjectDetails'


class TwitterChannelDetails(models.Model):

    bot = models.ForeignKey(Bot, null=True, blank=True,
                            on_delete=models.CASCADE)

    twitter_app_id = models.CharField(
        max_length=50, null=True, blank=True, default="", help_text="Twitter App ID")

    twitter_api_key = models.CharField(
        max_length=500, null=True, blank=True, default="", help_text="Twitter Api Key")

    twitter_key_api_secret = models.CharField(
        max_length=500, null=True, blank=True, default="", help_text="Twitter Key Api Secret")

    twitter_access_token = models.CharField(
        max_length=500, null=True, blank=True, default="", help_text="Twitter Access Token")

    twitter_access_token_secret = models.CharField(
        max_length=500, null=True, blank=True, default="", help_text="Twitter Access Token Secret")

    twitter_bearer_token = models.CharField(
        max_length=500, null=True, blank=True, default="", help_text="Twitter Bearer Token")

    twitter_dev_env_label = models.CharField(
        max_length=50, null=True, blank=True, default="", help_text="Twitter Developer Environment Name")

    twitter_webhook_id = models.CharField(
        max_length=50, null=True, blank=True, default="", help_text="Twitter Webhook ID")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'TwitterChannelDetails'
        verbose_name_plural = 'TwitterChannelDetails'


class TwitterTracker(models.Model):

    id_of_message = models.CharField(max_length=1000, unique=True, help_text="Twitter tracker")

    text_message = models.TextField(default="", help_text="Text message of bot")

    created_on = models.DateTimeField(default=timezone.now, help_text="Twittertracker object creation datetime")

    def __str__(self):
        return str(self.id_of_message) + " - " + str(self.text_message)

    class Meta:
        verbose_name = "TwitterTracker"
        verbose_name_plural = "TwitterTracker"


class IntentTreeHash(models.Model):

    tree = models.ForeignKey(Tree, null=True, blank=True,
                             on_delete=models.CASCADE)

    stem_words_name = models.CharField(
        max_length=5000, blank=True, null=True, help_text="Intent/Tree stem words name")

    hash_value = models.CharField(max_length=5000, default="", db_index=True, blank=True,
                                  null=True, help_text="Hashed value of intent/tree name ater removing stop words")

    is_tree = models.BooleanField(
        default=False, help_text='Designates whether it is a child tree and not intent')

    training_question = models.CharField(
        max_length=5000, blank=True, null=True, help_text="Training question associated with this intent tree hash")

    def __str__(self):
        return str(self.stem_words_name)

    class Meta:
        verbose_name = 'IntentTreeHash'
        verbose_name_plural = 'IntentTreeHash'


class FlowTerminationData(models.Model):

    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, help_text="User who terminated the flow", null=True, blank=True)

    created_datetime = models.DateTimeField(default=timezone.now)

    intent = models.ForeignKey(Intent, null=True, blank=True,
                               on_delete=models.CASCADE)

    tree = models.ForeignKey(Tree, null=True, blank=True,
                             on_delete=models.CASCADE)

    termination_message = models.TextField(default="", null=True, blank=True)

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.tree.name)

    class Meta:
        verbose_name = 'FlowTerminationData'
        verbose_name_plural = 'FlowTerminationData'


class UserFlowDropOffAnalytics(models.Model):

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Time of creation")

    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, help_text="User who dropped off from the flow", null=True, blank=True)

    intent_indentifed = models.ForeignKey(
        Intent, null=True, help_text="Intent of the flow", on_delete=models.CASCADE)

    previous_tree = models.ForeignKey(
        Tree, null=True, related_name="previous_tree_dropoff_analytics", help_text="Previous tree of the flow", on_delete=models.CASCADE)

    current_tree = models.ForeignKey(
        Tree, null=True, on_delete=models.CASCADE, help_text="Current tree of the flow")

    dropoff_type = models.CharField(
        choices=USER_DROPOFF_CHOICES, default=3, max_length=1, help_text="Type of dropoff of the flow")

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE, help_text="Channel of the flow")

    intent_name = models.TextField(
        default="", null=True, blank=True, help_text="Message in case of termination")

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'UserFlowDropOffAnalytics'
        verbose_name_plural = 'UserFlowDropOffAnalytics'


class SuggestedQueryHash(models.Model):

    query_hash = models.CharField(max_length=5000, default="", db_index=True, blank=True,
                                  null=True, help_text="Hashed value of query after removing stop words and  spell check")

    query_text = models.TextField(
        null=True, help_text="Message received by bot.")

    bot = models.ForeignKey(
        'Bot', blank=True, null=True, on_delete=models.SET_NULL, help_text="Bot Object whose hash info is stored")

    def __str__(self):
        return str(self.query_text)

    class Meta:
        verbose_name = 'SuggestedQueryHash'
        verbose_name_plural = 'SuggestedQueryHash'


class SuggestedQueryInfo(models.Model):

    intent_selected = models.ForeignKey(Intent, null=True, blank=True,
                                        on_delete=models.SET_NULL, help_text="")

    hash_info = models.ForeignKey(
        SuggestedQueryHash, null=True, blank=True, on_delete=models.CASCADE)

    count = models.IntegerField(default=0, blank=True, null=True,
                                help_text="count of this intent bieng selected for this query")

    def __str__(self):
        return str(self.intent_selected.name) + "--" + self.hash_info.query_text

    class Meta:
        verbose_name = 'SuggestedQueryInfo'
        verbose_name_plural = 'SuggestedQueryInfo'

    def is_threshold_crossed(self, bot_obj):
        try:
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj)

            if bot_info_obj.exists():
                bot_info_obj = bot_info_obj.first()
            else:
                import os
                words_file = os.path.join(
                    (os.path.abspath(os.path.dirname(__file__))), 'badwords.txt')
                with open(words_file, 'r') as f:
                    censor_list = [line.strip() for line in f.readlines()]
                bad_words = json.dumps(censor_list)
                bot_info_obj = bot_info_obj.create(
                    bot=bot_obj, bad_keywords=bad_words)

            threshold = bot_info_obj.suggested_intent_selected_threshold
            if self.count >= threshold:
                return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SuggestedQueryInfo > is_threshold_crossed %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

            return False


class AutoPopUpClickInfo(models.Model):

    name = models.CharField(
        max_length=200, help_text="Greeting/Intent bubble name.")

    bot = models.ForeignKey(Bot, null=True, blank=True, on_delete=models.CASCADE,
                            help_text="Bot with which click info is associated.")

    date = models.DateField(default=now, db_index=True,
                            help_text="Timestamp at which the auto popup greeting/intent bubble was clicked.")

    selected_language = models.ForeignKey(
        'Language', null=True, blank=True, on_delete=models.SET_NULL, help_text="Language selected by user (in whatsapp)")

    class Meta:
        verbose_name = "AutoPopUpClickInfo"
        verbose_name_plural = "AutoPopUpClickInfos"


class WelcomeBanner(models.Model):

    action_type = models.CharField(
        max_length=10, help_text="Type of action to be performed when clicked on welcome banner.")

    image_url = models.TextField(
        null=True, blank=True, help_text="Source of image.")

    redirection_url = models.TextField(
        null=True, blank=True, help_text="Redirection url to redirect.")

    intent = models.ForeignKey(Intent, null=True, blank=True, on_delete=models.CASCADE,
                               help_text="Intent to be triggered when clicked on welcome banner.")

    serial_number = models.IntegerField(
        null=True, blank=True, help_text="Serial number in welcome banner list.")

    bot_channel = models.ForeignKey(BotChannel, null=True, blank=True, on_delete=models.CASCADE,
                                    help_text="BotChannel with which this welcome banner is associated.")

    def get_intent_name(self):

        if self.intent == None:
            return "-"

        return self.intent.name

    def get_redirection_url(self):

        if self.redirection_url == None or self.redirection_url == "":
            return "-"

        return self.redirection_url

    def get_image_name(self):

        return str(self.image_url).strip().split("/")[-1]

    def get_intent_pk(self):

        if self.intent == None:
            return "None"

        return self.intent.pk

    class Meta:
        verbose_name = "WelcomeBanner"
        verbose_name_plural = "WelcomeBanner"


class EventProgress (models.Model):
    event_id = models.UUIDField(
        default=uuid.uuid4, editable=False)

    event_type = models.CharField(max_length=256,
                                  null=False,
                                  blank=False,
                                  choices=EVENT_CHOICES,
                                  help_text='Type of event which is tracked.')

    event_info = models.TextField(
        null=True, blank=True, default='{}', help_text="Contains event information in json format")

    user = models.ForeignKey(
        'EasyChatApp.User', null=True, blank=True, on_delete=models.SET_NULL)

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    event_progress = models.FloatField(
        default=0, null=True, blank=True, help_text="Event progress in percentage")

    is_completed = models.BooleanField(
        default=False, help_text='Designates whether event is completed or not')

    is_failed = models.BooleanField(
        default=False, help_text='Designates whether event is failed or not')

    failed_message = models.TextField(
        null=True, blank=True, default='', help_text="Failure message if event failed to complete")

    is_toast_displayed = models.BooleanField(
        default=False, help_text='Designates whether event completion toast is shown to user or not')

    event_datetime = models.DateTimeField(
        default=timezone.now, help_text='Date and time on which event was started')

    completed_datetime = models.DateTimeField(
        default=timezone.now, help_text='Date and time on which event was completed')

    time_taken = models.FloatField(
        default=0, null=True, blank=True, help_text="Time taken by event to complete (in seconds)")

    def __str__(self):
        try:
            return f'{str(self.event_type)} -- {str(self.event_progress)} -- {str(self.bot.name)}'
        except Exception:
            return 'Event'

    class Meta:
        verbose_name = "EventProgress"
        verbose_name_plural = "EventProgress"


class VoiceBotProfileDetail(models.Model):

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique session id for each cobrowsing session')

    bot = models.ForeignKey("EasyChatApp.Bot", null=False,
                            blank=False, on_delete=models.CASCADE)

    profile = models.ForeignKey(
        "EasyChatApp.Profile", null=True, blank=True, on_delete=models.SET_NULL)

    meta_data = models.TextField(default="{}", null=True, blank=True)

    end_event_meta_data = models.TextField(default="{}", null=True, blank=True)

    def __str__(self):
        return str(self.bot_id)

    class Meta:
        verbose_name = "VoiceBotProfileDetail"
        verbose_name_plural = "VoiceBotProfileDetail"


class VoiceBotConfiguration(models.Model):

    bot_channel = models.ForeignKey(
        BotChannel, null=False, blank=False, on_delete=models.CASCADE)

    api_key = models.TextField(default=DEFAULT_VOICE_BOT_API_KEY, null=True, blank=True, help_text="This is the API key required when campaigns are sent.")

    api_token = models.TextField(default=DEFAULT_VOICE_BOT_API_TOKEN, null=True, blank=True, help_text="This is the API token required when campaigns are sent.")

    api_subdomain = models.CharField(default=DEFAULT_VOICE_BOT_SUBDOMAIN, max_length=100, null=True, blank=True, choices=VOICE_BOT_SUBDOMAIN_CHOICES, help_text="It is the region of you account. For Mumbai it is 'api.in.exotel.com' and for singapore it is 'api.exotel.com'.")

    api_sid = models.CharField(default=DEFAULT_VOICE_BOT_SID, max_length=30, null=True, blank=True, help_text="This is the account sid required while sending the campaign.")

    silence_threshold_count = models.IntegerField(
        default=DEFAULT_SILENCE_THRESHOLD, null=True, blank=True, help_text="Voice bot repeat the silence_response this many times.")

    silence_response = models.TextField(default=DEFAULT_SILENCE_RESPONSE, null=True, blank=True,
                                        help_text="This response will be provided is silence voice event is detected.")

    silence_termination_response = models.TextField(default=DEFAULT_SILENCE_TERMINATION_RESPOSNE, null=True, blank=True,
                                                    help_text="This response will be provided if number of silence events exceeds the silence threshold count.")

    loop_threshold_count = models.IntegerField(default=DEFAULT_LOOP_THRESHOLD, null=True,
                                               blank=True, help_text="Voice Bot will detect loop response is response is repeated.")

    is_agent_handover = models.BooleanField(
        default=DEFAULT_AGENT_HANDOVER, help_text="If this is enabled then transfer loop response will be provided if loop count exceeds loop threshold count.")

    loop_termination_response = models.TextField(default=DEFAULT_LOOP_TERMINATION_RESPONSE, null=True, blank=True,
                                                 help_text="If agent handover is false then this response will be provided and call will be ended.")

    loop_handover_response = models.TextField(default=DEFAULT_LOOP_AGENT_HANDOVER_RESPONSE, null=True,
                                              blank=True, help_text="If agent handover is true this response will be provided.")

    silence_event_trigger_timeout = models.IntegerField(
        default=DEFAULT_SILENCE_EVENT_TRIGGER_TIMEOUT, help_text="This designates the time period after which silence event will be triggers if user doesn't response.")

    fallback_response = models.TextField(
        default=DEFAULT_FALLBACK_RESPONSE, help_text="The bot will reply with fallback response if the detected language does not exist in supported languages for voice channel.")

    def __str__(self):
        return str(self.bot_channel)

    class Meta:
        verbose_name = "VoiceBotConfiguration"
        verbose_name_plural = "VoiceBotConfigurations"


class RCSDetails(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    rcs_credentials_file_path = models.TextField(default="",
                                                 blank=True, null=True, help_text="file path of the api credentials file")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'RCSDetail'
        verbose_name_plural = 'RCSDetails'


class RCSMessageDetails(models.Model):

    message_id = models.TextField(
        default="", blank=True, help_text="message id received from rcs message ")

    def __str__(self):
        return str(self.message_id)

    class Meta:
        verbose_name = 'RCSMessageDetail'
        verbose_name_plural = 'RCSMessageDetails'


class FormWidgetFieldProcessor(models.Model):

    field_id = models.CharField(
        default="", max_length=5000, help_text='Field ID', primary_key=True)

    name = models.CharField(default="FunctionName",
                            max_length=100, help_text="Function name")

    function = models.TextField(
        default="def f(x):\n    return x", null=True, blank=True, help_text="Function code")

    processor_lang = models.CharField(max_length=256,
                                      default="1",
                                      null=True,
                                      blank=True,
                                      choices=LANGUAGE_CHOICES, help_text="Programming language of the code.")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'FormWidgetFieldProcessor'
        verbose_name_plural = 'FormWidgetFieldProcessors'


class EmojiBotResponse(models.Model):
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    add_livechat_intent = models.TextField(
        default='{"angry": "True", "happy": "False", "neutral": "False", "sad": "True"}', help_text="Designates whether the response shows livechat recommendation w.r.t type of response")

    emoji_angry_response_text = models.CharField(
        max_length=500, default="<p>I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.</p>", help_text="emoji response text message based on emoji type.")

    emoji_happy_response_text = models.CharField(
        max_length=500, default="<p>Thank you. I'm here to help you with anything else you need 😄</p>", help_text="emoji response text message based on emoji type.")

    emoji_neutral_response_text = models.CharField(
        max_length=500, default="<p>Hi, I am Iris, a Virtual Assistant. I am here to help you with your most common queries. You name it and I do it. How can I help you today?</p>", help_text="emoji response text message based on emoji type.")

    emoji_sad_response_text = models.CharField(
        max_length=500, default="<p>I am always serious. I'm really sorry if I couldn't handle your query correctly. I am an automated assistant that learns gradually. How else may I assist you?</p>", help_text="emoji response text message based on emoji type.")

    def __str__(self):
        try:
            return str(self.bot.name) + " - " + str(self.bot.pk)
        except Exception:
            return 'Emoji'

    class Meta:
        verbose_name = "EmojiBotResponse"
        verbose_name_plural = "EmojiBotResponse"


class ProfanityBotResponse(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    is_suggest_livechat_for_profanity_words_enabled = models.BooleanField(
        default=False, help_text="Designates whether or not to suggest livechat functionality enabled")

    profanity_response_text = models.CharField(
        max_length=500, default="<p>I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.</p>", help_text="profanity response text")

    add_livechat_as_quick_recommendation = models.BooleanField(
        default=True, help_text="designates whether to show livechat as a quick recommendations")

    trigger_livechat_intent = models.BooleanField(
        default=False, help_text="Designates whether or not to trigger livechat intent")

    def __str__(self):
        try:
            return 'Profanity Response For -' + str(self.bot.name) + " - " + str(self.bot.pk)
        except Exception:
            return 'Profanity Response'

    class Meta:
        verbose_name = "ProfanityBotResponse"
        verbose_name_plural = "ProfanityBotResponse"


class LanguageApiFailureLogs(models.Model):

    text = models.TextField(
        null=True, blank=True, default='', help_text="text for which Api Failed")

    meta_data = models.TextField(
        null=True, blank=True, default='', help_text="Meta Data related to Failure of Translation Api")

    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        try:
            return 'LanguageApiFailureLog -' + str(self.text) + " - " + str(self.timestamp)
        except Exception:
            return 'LanguageApiFailureLog'

    class Meta:
        verbose_name = "LanguageApiFailureLog"
        verbose_name_plural = "LanguageApiFailureLogs"


class EasyChatAuthToken(models.Model):

    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique access token key')

    user = models.ForeignKey(
        'EasyChatApp.User', null=True, blank=False, on_delete=models.CASCADE, help_text='Foreign key of user to which the token belongs')

    is_expired = models.BooleanField(
        default=False, null=False, blank=False, help_text='Designates whether the token is expired or not.')

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when EasyChat Auth Token is created.")

    last_accessed_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when EasyChat Auth token was last used it is only updated once in a minute")

    api_used_in_last_minute = models.IntegerField(
        default=1, null=True, blank=True, help_text="Number of times the external api is used in last minute .This field is for applying rate limiting")

    def is_rate_limit_exceeded(self):
        if self.api_used_in_last_minute > RATE_LIMIT_FOR_EXTERNAL_API_IN_ONE_MINUTE:
            return True

        return False

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'EasyChatAuthToken'
        verbose_name_plural = 'EasyChatAuthTokens'


class EasyChatExternalAPIAuditTrail(models.Model):

    request_id = models.UUIDField(default=uuid.uuid4,
                                  editable=False, help_text='Request ID generated while accessing external API')

    token = models.ForeignKey(
        'EasyChatApp.EasyChatAuthToken', null=True, on_delete=models.SET_NULL, help_text='Foreign key to auth token')

    status_code = models.CharField(
        default="500", null=True, blank=True, help_text="Status code of the API Response sent to the user.", max_length=10)

    access_type = models.CharField(
        max_length=256, null=True, blank=True, choices=AUTH_TOKEN_ACCESS_TYPE_CHOICES, help_text="Type of data requested by user")

    request_data = models.TextField(
        default="{}", null=True, blank=True, help_text="Request data received from API call")

    response_data = models.TextField(
        default="{}", null=True, blank=True, help_text="API Response sent to the user")

    metadata = models.TextField(
        default="{}", null=True, blank=True, help_text="Metadata of the request received")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when external API is used.")

    def __str__(self):
        return str(self.request_id)

    class Meta:
        verbose_name = 'EasyChatExternalAPIAuditTrail'
        verbose_name_plural = 'EasyChatExternalAPIAuditTrails'


class EasyChatCronjobTracker(models.Model):

    function_id = models.CharField(max_length=100, null=False,
                                   help_text="Function id of a cronjob function which is running")
    
    creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the cronjob tracker object was created')
        
    class Meta:
        verbose_name = "EasyChatCronjobTracker"
        verbose_name_plural = "EasyChatCronjobTrackers"

    def __str__(self):
        return self.function_id


class CustomIntentBubblesForWebpages(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    custom_intent_bubble = models.ManyToManyField(
        'Intent', blank=True, help_text="Intents for this custom intent bubble.")

    web_page = models.TextField(default="", help_text="Website visited")

    custom_intents_for = models.CharField(max_length=256, default=AUTO_POPUP, null=False, blank=False,
                                          choices=CUSTOM_INTENTS_CHOICE, help_text='Designates whether this data is of form assist or auto popup or etc')

    def __str__(self):
        return str(self.pk) + "-" + str(self.bot.name) + "-" + str(self.web_page)

    class Meta:
        verbose_name = 'CustomIntentBubblesForWebpage'
        verbose_name_plural = 'CustomIntentBubblesForWebpages'


class WhatsAppMenuSection(models.Model):

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, help_text="It designates with which tree the menu section is associated.")

    title = models.CharField(default="Section title", max_length=24, null=False, blank=False, help_text="Section title name")

    child_trees = models.TextField(default="[]", null=True, blank=True, help_text="The child trees associated with this section.")

    main_intents = models.TextField(default="[]", null=True, blank=True, help_text="The main intents associated with this section.")

    def get_child_tree_details(self, src="en"):
        try:
            from EasyChatApp.utils import get_intent_obj_from_tree_obj, get_parent_tree_obj

            if self.child_trees and self.tree.is_child_tree_visible:
                child_trees = json.loads(self.child_trees)

                child_trees_data = []

                updated_child_trees_list = []

                for child_tree in child_trees:
                    child_tree_data = {}
                    tree_obj = Tree.objects.filter(pk=child_tree, is_deleted=False).first()
                    if tree_obj:

                        child_tree_data["tree_pk"] = tree_obj.pk
                        child_tree_data["name"] = tree_obj.name
                        child_tree_data["short_name"] = tree_obj.get_whatsapp_short_name()
                        child_tree_data["description"] = tree_obj.get_whatsapp_description()
                        
                        intent_obj = get_intent_obj_from_tree_obj(tree_obj)
                        child_tree_data["intent_pk"] = ""

                        if intent_obj:
                            child_tree_data["intent_pk"] = str(intent_obj.pk)

                        parent_tree_obj = get_parent_tree_obj(tree_obj)
                        child_tree_data["parent_tree_pk"] = ""

                        if parent_tree_obj:
                            child_tree_data["parent_tree_pk"] = str(parent_tree_obj.pk)

                        child_trees_data.append(child_tree_data)
                        updated_child_trees_list.append(child_tree)

                if updated_child_trees_list != child_trees:
                    self.child_trees = json.dumps(updated_child_trees_list)
                    self.save(update_fields=["child_trees"])

                return child_trees_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_child_tree_details %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

        return []

    def get_main_intent_details(self):
        try:
            if self.main_intents:
                main_intents = json.loads(self.main_intents)
                main_intents_data = []

                updated_main_intents_list = []

                for main_intent in main_intents:
                    main_intent_data = {}
                    intent_obj = Intent.objects.filter(pk=main_intent, is_deleted=False, is_hidden=False, is_small_talk=False).first()
                    if intent_obj:
                        main_intent_data["intent_pk"] = str(intent_obj.pk)
                        main_intent_data["name"] = intent_obj.tree.name
                        main_intent_data["short_name"] = intent_obj.tree.get_whatsapp_short_name()
                        main_intent_data["description"] = intent_obj.tree.get_whatsapp_description()

                        main_intents_data.append(main_intent_data)
                        updated_main_intents_list.append(main_intent)

                if main_intents != updated_main_intents_list:
                    self.main_intents = json.dumps(updated_main_intents_list)
                    self.save(update_fields=["main_intents"])

                return main_intents_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_main_intent_details %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

        return []

    def __str__(self):
        return str(self.tree.name) + "-" + str(self.title)

    class Meta:
        verbose_name = 'WhatsAppMenuSection'
        verbose_name_plural = 'WhatsAppMenuSections'


class FusionProcessor(models.Model):
    name = models.CharField(default="",
                            max_length=100, help_text="Function name")

    function = models.TextField(
        default="def f(x):\n    return x", null=True, blank=True, help_text="Function code")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'FusionProcessor'
        verbose_name_plural = 'FusionProcessor'


class BotFusionConfigurationProcessors(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=False,
                            blank=False, on_delete=models.CASCADE)

    app_id = models.TextField(default="", null=True, blank=True, help_text="Unique App ID given by ameyo fusion.")

    host_name = models.TextField(default="", null=True, blank=True, help_text="Host and Port given by ameyo fusion.")

    bot_chat_history_processor = models.ForeignKey(
        FusionProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Fusion bot chat history processor.", related_name="BotChatHistoryProcessor")

    text_message_processor = models.ForeignKey(
        FusionProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Fusion text message processor.", related_name="TextMessageProcessor")

    attachment_message_processor = models.ForeignKey(
        FusionProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Fusion attachment message processor.", related_name="AttachmentMessageProcessor")

    chat_disconnect_processor = models.ForeignKey(
        FusionProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Fusion chat disconnect processor.", related_name="ChatDisconnectedProcessor")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'BotFusionConfigurationProcessors'
        verbose_name_plural = 'BotFusionConfigurationProcessors'


class WhatsappCredentialsConfig(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL, help_text="Bot to which this Credentials belongs")

    username = models.CharField(max_length=100, null=True,
                                   blank=True, help_text="WhatsApp Vendor Credentials Username")

    password = models.CharField(max_length=256, null=True,
                                   blank=True, help_text="WhatsApp Vendor Credentials password")
    
    host_url = models.CharField(max_length=500, null=True,
                                   blank=True, help_text="WhatsApp Vendor Credentials host url")

    def __str__(self):
        return str(self.bot.name) + "-" + str(self.username)

    class Meta:
        verbose_name = 'WhatsappCredentialsConfig'
        verbose_name_plural = 'WhatsappCredentialsConfig'


class WhatsappCatalogueDetails(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL, help_text="Bot to which this catalogue belongs")

    catalogue_type = models.CharField(max_length=40, default=COMMERCE_MANAGER_CATALOGUE_CHOICE, null=False, blank=False,
                                      choices=WHATSAPP_CATALOGUE_TYPES, help_text='Type of catalogue selected (Commerce Manager/API Based)')

    catalogue_id = models.CharField(max_length=50, null=True,
                                    blank=True, help_text="WhatsApp Product Catalogue ID.")

    business_id = models.CharField(max_length=50, null=True,
                                   blank=True, help_text="WhatsApp Business ID with which Catalogue is linked.")

    access_token = models.CharField(max_length=500, null=True,
                                    blank=True, help_text="User Access Token required for accessing WhatsApp Catalogue APIs")

    catalogue_metadata = models.TextField(
        default="{}", null=True, blank=True, help_text="Details of Catalogue")

    is_catalogue_enabled = models.BooleanField(
        default=False, help_text="Designates whether WhatsApp Catalogue is enabled or not.")

    def __str__(self):
        return str(self.bot.name) + "-" + str(self.catalogue_type)

    class Meta:
        verbose_name = 'WhatsappCatalogueDetails'
        verbose_name_plural = 'WhatsappCatalogueDetails'


class UserSessionHealth(models.Model):

    creation_date = models.DateField(
        default=now, db_index=True, help_text="Date of creation of user session health")

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    profile = models.ForeignKey('EasyChatApp.Profile', null=True,
                                blank=True, on_delete=models.SET_NULL)
    
    session_id = models.CharField(
        max_length=100, null=False, blank=False, help_text="Session id")

    block_type = models.CharField(
        max_length=20, null=True, blank=True, choices=BLOCK_TYPE_CHOICES, help_text="Designates which type of block user got")

    blocked_spam_keywords = models.TextField(
        default="", null=True, blank=True, help_text="Comma separated spam keywords")

    spam_keywords_count = models.IntegerField(
        default=0, help_text="Count of spam keywords")

    message_queries_count = models.IntegerField(
        default=0, help_text="Count of message queries")

    is_blocked = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether the user session is blocked or not")

    block_time = models.DateTimeField(
        null=True, blank=True, help_text="Designates when the user gets blocked in a session")

    unblock_time = models.DateTimeField(
        null=True, blank=True, help_text="Designates when user will get unblocked in a session")

    def __str__(self):
        return str(self.profile.user_id) + "-" + str(self.session_id)

    def save(self, *args, **kwargs):
        if self.pk:
            old_user_session_health = self.__class__.objects.get(pk=self.pk)

            if old_user_session_health.is_blocked != self.is_blocked:
                if self.is_blocked == False and timezone.now() < self.unblock_time:
                    self.block_type = None
                    self.blocked_spam_keywords = ""
                    self.spam_keywords_count = 0
                    self.message_queries_count = 0
                    self.block_time = None
                    self.unblock_time = None
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'UserSessionHealth'
        verbose_name_plural = 'UserSessionsHealth'


class BlockConfig(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL)

    is_block_spam_user_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether Block Spam User is enabled")

    is_block_based_on_user_queries_enabled = models.BooleanField(
        default=True, null=False, blank=False, help_text="Designates whether Block Based on User Queries is enabled")

    is_block_based_on_spam_keywords_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether Block Based on Spam Keywords is enabled")

    spam_keywords = models.TextField(
        default="", null=True, blank=True, help_text="Comma separated spam keywords")

    user_query_warning_thresold = models.IntegerField(
        default=100, help_text="Thresold value for query warning")

    user_query_warning_message_text = models.TextField(
        default="⚠️ Warning Message: It seems you are spamming messages, request you to please do not spam more messages, or else we will block you.",
        null=False, blank=False, help_text="Message to display when user crosses query warning thresold")

    user_query_block_thresold = models.IntegerField(
        default=101, help_text="Thresold value for query block")

    user_query_block_message_text = models.TextField(
        default="You are blocked for 12 hours due to spamming a lot of messages.",
        null=False, blank=False, help_text="Message to display when user crosses query block thresold")

    user_query_block_duration = models.IntegerField(
        default=12, null=False, blank=False, help_text="Designates for query spam how many hours the user will be blocked")

    spam_keywords_warning_thresold = models.IntegerField(
        default=1, help_text="Thresold value for spam keywords warning")

    spam_keywords_warning_message_text = models.TextField(
        default="⚠️ Warning Message: It seems you are using harmful words, request you to please do not use such type of keywords in queries, or else we will block you.",
        null=False, blank=False, help_text="Message to display when user crosses spam keywords warning thresold")

    spam_keywords_block_thresold = models.IntegerField(
        default=2, help_text="Thresold value for spam keywords block")

    spam_keywords_block_message_text = models.TextField(
        default="You are blocked for 12 hours due to using harmful keywords in the query.",
        null=False, blank=False, help_text="Message to display when user crosses spam keywords block thresold")

    spam_keywords_block_duration = models.IntegerField(
        default=12, null=False, blank=False, help_text="Designates for spam keywords how many hours the user will be blocked")

    def __str__(self):
        return str(self.bot.name) + "(" + str(self.bot.pk) + ")" + "-" + "block_config"

    class Meta:
        verbose_name = 'BlockConfig'
        verbose_name_plural = 'BlockConfigs'


class WhatsappCatalogueCart(models.Model):

    user = models.ForeignKey(
        'Profile', null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text='Foreign Key to Profile Object of the cart user.')

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, on_delete=models.SET_NULL, help_text="Bot to which this Catlaogue Cart belongs")

    current_cart_packet = models.TextField(
        default="{}", null=True, blank=True, help_text="Current packet of the user's cart")

    pending_cart_packet = models.TextField(
        default="{}", null=True, blank=True, help_text="Pending packet of the user's cart")

    cart_total = models.CharField(
        max_length=50, default="", null=True, blank=True, help_text="Price total of the current cart packet")

    is_purchased = models.BooleanField(
        default=False, help_text="Designates whether this cart has been purchased/processed or not")

    cart_update_time = models.DateTimeField(
        default=timezone.now, help_text="Datetime when the cart was updated last time")

    def __str__(self):
        return str(self.user.user_id) + "-" + str(self.bot.name)

    class Meta:
        verbose_name = 'WhatsappCatalogueCart'
        verbose_name_plural = 'WhatsappCatalogueCarts'


class WhatsappCatalogueItems(models.Model):

    catalogue_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Catalogue ID of the item under which it is present")

    item_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Unique Item ID of the product")

    item_name = models.TextField(
        default="-", null=True, blank=True, help_text="Name of the Item")

    retailer_id = models.CharField(
        max_length=100, default="-", null=True, blank=True, help_text="Retailer/Content Id of the Item")

    brand = models.CharField(
        max_length=100, default="-", null=True, blank=True, help_text="Brand of the Item")

    price = models.FloatField(
        max_length=50, default="", null=True, blank=True, help_text="Price of the Item")

    currency = models.CharField(
        max_length=50, default="-", null=True, blank=True, help_text="Currency in which item's price is set")

    availability = models.CharField(
        max_length=50, default="-", null=True, blank=True, help_text="Availability of item (eg Out of stock, In Stock)")
    
    gender = models.CharField(
        max_length=50, default="-", null=True, blank=True, help_text="Suitable gender for the Item")

    condition = models.CharField(
        max_length=50, default="-", null=True, blank=True, help_text="Condition of the item (eg New, Old)")

    image_url = models.TextField(
        default="-", null=True, blank=True, help_text="Image URL of the product")

    item_details = models.TextField(
        default="{}", null=True, blank=True, help_text="Details data dump of the item")

    preview_image_urls = models.TextField(
        default="[]", null=True, blank=True, help_text="Images of items to display on our console. These images will be stored on our server")
    
    def __str__(self):
        return str(self.catalogue_id) + " - " + self.item_name

    class Meta:
        verbose_name = 'WhatsappCatalogueItems'
        verbose_name_plural = 'WhatsappCatalogueItems'


class EasyChatFileCaching(models.Model):

    original_url = models.TextField(
        default="", null=True, blank=True, help_text="URL of the media which is cached")

    url_hash = models.TextField(
        default="", null=True, blank=True, help_text="Hash of the URL cached")

    file_path = models.TextField(
        default="", help_text="File path of the media after caching")

    file_url = models.TextField(
        default="", help_text="Server file URL after caching")

    created_on = models.DateTimeField(
        default=timezone.now, help_text="Datetime when the media was cached")

    def __str__(self):
        return str(self.original_url)

    class Meta:
        verbose_name = 'EasyChatFileCaching'
        verbose_name_plural = 'EasyChatFileCaching'


class WhatsAppVendorConfig(models.Model):

    wsp_name = models.CharField(max_length=20, null=False, blank=False,
                                choices=WSP_CHOICES, help_text="Name of WhatsApp Service Provider")

    mobile_number = models.CharField(
        max_length=100, null=True, blank=True, help_text="WhatsApp number associated with the object")

    username = models.CharField(max_length=256, null=True,
                                blank=True, help_text="WhatsApp Vendor Credentials Username")

    password = models.CharField(max_length=256,
                                null=True,
                                blank=True,
                                help_text='WhatsApp Vendor Credentials Password')

    session_api_host = models.CharField(max_length=256,
                                        null=False,
                                        blank=False,
                                        help_text='WhatsApp Vendor API host Url (required)')

    dynamic_token = models.TextField(
        default="token", help_text="WhatsApp API token key")

    token_updated_on = models.DateTimeField(
        default=timezone.now, help_text="Datetime when the token was last updated")

    dynamic_token_refresh_time = models.IntegerField(
        default=6, null=True, blank=True, help_text="Minimum Days after which token should be refreshed")

    def __str__(self):
        return str(self.session_api_host) + " - " + str(self.get_wsp_name_display())

    class Meta:
        verbose_name = 'WhatsAppVendorConfig'
        verbose_name_plural = 'WhatsAppVendorConfig'


class DailyLiveChatAnalytics(models.Model):

    bot = models.ForeignKey(Bot, null=True, blank=True, on_delete=models.CASCADE, help_text="Bot with which this analytics is associated.")

    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.CASCADE, help_text="Channel with which this analytics is associated.")

    date = models.DateField(default=now, help_text="Date with which this analytics is associated.", db_index=True)

    count = models.IntegerField(default=0, help_text="Total number of time the livechat intent is triggered.")

    def __str__(self):
        return str(self.date) + " - " + str(self.bot)

    class Meta:
        verbose_name = 'DailyLiveChatAnalytics'
        verbose_name_plural = 'DailyLiveChatAnalytics'
