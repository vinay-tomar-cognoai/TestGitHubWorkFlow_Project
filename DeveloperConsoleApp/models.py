from django.db import models
from DeveloperConsoleApp.constants import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

from EasyChat.settings import BASE_DIR

import json
import uuid
import os


class DeveloperConsoleConfig(models.Model):

    masking_pii_data_otp_email = models.TextField(
        default=json.dumps(MASKING_PII_DATA_OTP_EMAIL), null=True, blank=True, help_text="Email IDs to which masking pii data otp email has to be sent")

    cronjob_report_email = models.TextField(
        default=json.dumps(CRONJOB_REPORT_EMAIL), null=True, blank=True, help_text="Email IDs to which cronjob report email has to be sent")

    email_api_end_point = models.TextField(default=DEFAULT_EMAIL_END_POINT, null=True, blank=True, help_text="Email end point through which emails will be sent.")

    email_host_user = models.CharField(
        default=EMAIL_HOST_USER, max_length=255, null=True, blank=True, help_text="Email ID of the host user")

    email_host_password = models.CharField(
        default=EMAIL_HOST_PASSWORD, max_length=255, null=True, blank=True, help_text="Password of the email host user")

    csm_email_id = models.CharField(
        default=EMAIL_CSM, max_length=255, null=True, blank=True, help_text="Email ID of the CSM team")

    notification_email_id = models.CharField(
        default=EMAIL_NOTIFICATIONS, max_length=255, null=True, blank=True, help_text="Email ID for the notification")

    show_console_logs = models.BooleanField(
        default=False, help_text="Show Javascript console logs")

    wrong_password_lockin_timeout = models.IntegerField(
        default=WRONG_PASSWORD_LOCKIN_TIME, null=True, blank=True, help_text="Lock-in timeout (in mins) in case of wrong password attempt")

    wrong_password_attempts = models.IntegerField(
        default=TOTAL_WRONG_PASSWORD_ATTEMPTS, null=True, blank=True, help_text="Total number of wrong password attempts")

    email_api_failure_message = models.TextField(
        default=EMAIL_API_FAILURE_MESSAGE, null=True, blank=True)

    google_translation_api_failure_message = models.TextField(
        default=GOOGLE_TRANSLATION_API_FAILURE_MESSAGE, null=True, blank=True)

    tiny_url_api_token = models.TextField(
        default=TINY_URL_API_TOKEN, null=True, blank=True)

    save_file_into_s3_bucket = models.BooleanField(
        default=False, help_text="Enabling it will save files in s3 bucket instead of local files"
    )

    aws_user_name = models.TextField(
        default=AWS_USER_NAME, null=True, blank=True)

    aws_password = models.TextField(
        null=True, blank=True)

    aws_access_key_id = models.TextField(
        default=AWS_ACCESS_KEY_ID, null=True, blank=True)

    aws_secret_access_key = models.TextField(
        default=AWS_SECRET_ACCESS_KEY, null=True, blank=True)

    aws_s3_bucket_name = models.TextField(
        default=AWS_S3_BUCKET_NAME, null=True, blank=True)

    login_logo = models.CharField(max_length=300, default=GENERAL_LOGIN_LOGO, null=False, blank=False)
    
    general_page_logo = models.CharField(max_length=300, default=GENERAL_PAGE_LOGO, null=False, blank=False)

    reset_password_details_expire_after = models.IntegerField(
        default=60, help_text="Reset Password link and Otp for reset password expire after this much time in minutes")

    authentication_otp_expire_after = models.IntegerField(
        default=10, help_text="Otp for multi-factor authentication expire after this much time in minutes")

    primary_color = models.CharField(
        default=CONSOLE_PRIMARY_COLOR, null=False, blank=False, max_length=6)

    secondary_color = models.CharField(
        default=CONSOLE_SECONDARY_COLOR, null=False, blank=False, max_length=6)

    hide_login_with_gsuite = models.BooleanField(default=False)

    general_favicon = models.CharField(max_length=300, default=GENERAL_FAVICON, null=False, blank=False)

    general_title = models.CharField(max_length=300, default=GENERAL_TITLE)

    replace_easychat_over_console = models.CharField(max_length=300, default="EasyChat")

    enable_footer_over_entire_console = models.BooleanField(default=True)

    legal_name = models.CharField(max_length=300, default=LEGAL_NAME)

    custom_report_template_signature = models.TextField(
        default=DEFAULT_CUSTOM_REPORT_TEMPLATE_SIGNATURE, null=True, blank=True)

    livechat_config = models.ForeignKey('LiveChatAppConfig', blank=True, null=True, on_delete=models.SET_NULL)

    spell_check_api_endpoint = models.TextField(default=DEFAULT_SPELL_CHECK_API_ENDPOINT)

    spell_check_api_username = models.TextField(default=DEFAULT_SPELL_CHECK_API_USERNAME)

    spell_check_api_password = models.TextField(default=DEFAULT_SPELL_CHECK_API_PASSWORD)

    add_spell_check_words_api_endpoint = models.TextField(default=DEFAULT_ADD_SPELL_CHECK_WORDS_API_ENDPOINT)

    remove_spell_check_words_api_endpoint = models.TextField(default=DEFAULT_REMOVE_SPELL_CHECK_WORDS_API_ENDPOINT, help_text="Spell checker endpoint for removing words")

    edit_spell_check_words_api_endpoint = models.TextField(default=DEFAULT_EDIT_SPELL_CHECK_WORDS_API_ENDPOINT, help_text="Spell checker endpoint for editing words")

    whitelisted_ip_addresses = models.TextField(null=True, blank=True, help_text="Add the ip addresses comma separated if you want to whitelist that ip address else keep it blank.")

    sso_metadata_content = models.TextField(default=DEFAULT_SSO_METADATA_CONTENT, null=True, blank=True, help_text="Add the sso metadata content over here.")

    advanced_faq_extraction = models.BooleanField(
        default=True, help_text="If enabled, FAQs will be extracted using Selenium method. This may slow down other operations while FAQs are being extracted.")
    
    disabled_multifactor_authentication = models.BooleanField(default=False, help_text="Multi-factor authentication for login")

    ameyo_fusion_url = models.TextField(default=DEFAULT_AMEYO_FUSION_URL, help_text="Ameyo fusion URL.")

    def get_cronjob_report_email(self):
        try:
            cronjob_report_email = json.loads(self.cronjob_report_email)
            return cronjob_report_email
        except Exception:
            return []

    def get_masking_pii_data_otp_emails(self):
        try:
            masking_pii_data_otp_email = json.loads(
                self.masking_pii_data_otp_email)
            return masking_pii_data_otp_email
        except Exception:
            return []

    def get_whitelisted_ip_addresses(self):
        try:
            if self.whitelisted_ip_addresses:
                return [ip_address.strip() for ip_address in str(self.whitelisted_ip_addresses).strip().split(",") if ip_address.strip() != ""]
            return []
        except Exception:
            return []

    def __str__(self):
        return "Config"

    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Config"


@receiver(post_save, sender=DeveloperConsoleConfig)
def set_developer_console_object_cache(sender, instance, **kwargs):
    cache.set("DeveloperConsoleConfigObject", instance, settings.CACHE_TIME)


@receiver(post_save, sender=DeveloperConsoleConfig)
def update_sso_metadata_content(sender, instance, **kwargs):
    sso_metadata_content = ""
    if instance.sso_metadata_content:
        sso_metadata_content = instance.sso_metadata_content

    metadata_file_path = os.path.join(BASE_DIR) + '/google-ldap.conf'

    metadata_file = open(metadata_file_path, "w")

    metadata_file.write(sso_metadata_content)

    metadata_file.close()


class CentralisedFileAccessManagement(models.Model):

    key = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text="unique access token key")

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True, help_text="Original name of file without adding any marker to make it unique")

    aws_s3_object_name = models.TextField(
        null=True, blank=True, help_text="AWS S3 bucket object name to uniquely identify file")

    def __str__(self):
        return str(self.key)

    class Meta:
        verbose_name = 'CentralisedFileAccessManagement'
        verbose_name_plural = 'CentralisedFileAccessManagement'


class EasyChatAppConfig(models.Model):

    chatbot_logo = models.CharField(max_length=300, default=DEFAULT_CHATBOT_LOGO, null=False, blank=False)

    tab_logo = models.CharField(max_length=300, default=DEFAULT_CHATBOT_TAB_LOGO, null=False, blank=False)

    title_text = models.CharField(max_length=50, default=DEFAULT_CHATBOT_TITLE_TEXT, null=False, blank=False)

    disable_show_brand_name = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'EasyChatAppConfig'
        verbose_name_plural = 'EasyChatAppConfig'
    

class LiveChatAppConfig(models.Model):

    livechat_logo = models.TextField(
        default="/static/DeveloperConsoleApp/img/livechat-logo.png", null=False, blank=False)

    livechat_favicon = models.TextField(
        default="/static/DeveloperConsoleApp/img/livechat-favicon.png", null=False, blank=False)

    livechat_title = models.CharField(
        max_length=50, default="Cogno LiveChat", null=False, blank=False)

    livechat_masking_pii_data_otp_email = models.TextField(
        default=json.dumps(MASKING_PII_DATA_OTP_EMAIL), null=True, blank=True, help_text="Email IDs to which masking pii data otp email has to be sent")

    def __str__(self):
        return "LiveChatAppConfig"

    class Meta:
        verbose_name = 'LiveChatAppConfig'
        verbose_name_plural = 'LiveChatAppConfig'


class CognoDeskAppConfig(models.Model):

    chatbot_logo = models.CharField(max_length=300, default=DEFAULT_DESK_LOGO, null=False, blank=False)

    tab_logo = models.CharField(max_length=300, default=DEFAULT_DESK_TAB_LOGO, null=False, blank=False)

    title_text = models.CharField(max_length=50, default=DEFAULT_DESK_TITLE_TEXT, null=False, blank=False)

    class Meta:
        verbose_name = 'CognoDeskAppConfig'
        verbose_name_plural = 'CognoDeskAppConfig'


class CobrowsingAppConfig(models.Model):

    cobrowsing_logo = models.TextField(default=DEFAULT_COBROWSING_LOGO, null=False, blank=False)

    cobrowsing_favicon = models.TextField(default=DEFAULT_COBROWSING_TAB_LOGO, null=False, blank=False)

    cobrowsing_title_text = models.TextField(default=DEFAULT_COBROWSING_TITLE_TEXT, null=False, blank=False)

    cobrowsing_masking_pii_data_otp_email = models.TextField(
        default=json.dumps(MASKING_PII_DATA_OTP_EMAIL), null=True, blank=True, help_text="Email IDs to which masking pii data otp email will be sent")

    class Meta:
        verbose_name = 'CobrowsingAppConfig'
        verbose_name_plural = 'CobrowsingAppConfig'

    def __str__(self):
        return "CobrowsingAppConfig"


class CognoMeetAppConfig(models.Model):

    cognomeet_logo = models.TextField(default=DEFAULT_COGNOMEET_LOGO, null=False, blank=False)

    cognomeet_favicon = models.TextField(default=DEFAULT_COGNOMEET_TAB_LOGO, null=False, blank=False)

    cognomeet_title_text = models.TextField(default=DEFAULT_COGNOMEET_TITLE_TEXT, null=False, blank=False)

    class Meta:
        verbose_name = 'CognoMeetAppConfig'
        verbose_name_plural = 'CognoMeetAppConfig'

    def __str__(self):
        return "CognoMeetAppConfig"
