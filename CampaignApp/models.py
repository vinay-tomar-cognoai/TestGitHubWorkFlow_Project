from django.db import models
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.functions import Length

from CampaignApp.encrypt import CustomEncrypt
from EasyChatApp.models import Bot, User
from CampaignApp.constants import *
from EasyChatApp.constants import WSP_CHOICES
from EasyChatApp.utils import get_intent_obj_from_tree_obj, get_parent_tree_obj

# Create your models here.
import sys
import json
import uuid
import logging
import hashlib
import datetime
import string
import random

logger = logging.getLogger(__name__)


class CampaignAnalytics(models.Model):

    total_audience = models.IntegerField(default=0)

    message_sent = models.IntegerField(default=0)

    message_read = models.IntegerField(default=0)

    message_delivered = models.IntegerField(default=0)

    message_unsuccessful = models.IntegerField(default=0)

    message_replied = models.IntegerField(default=0, help_text='number of replies got from campaign')

    message_processed = models.IntegerField(default=0, help_text='number of audience entries processed while sending campaign')

    test_message_sent = models.IntegerField(default=0, help_text='number of test sent from campaign')

    test_message_unsuccessful = models.IntegerField(default=0, help_text='number of test failed from campaign')

    total_tested = models.IntegerField(default=0, help_text='number of total test campaign')

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        if self.campaign:
            return self.campaign.name + " - " + str(self.total_audience)
        else:
            return "None - " + str(self.total_audience)

    def open_rate(self):
        # to be implemented
        if self.message_sent == 0:
            return 0
        else:
            return round(self.message_read / self.message_sent * 100, 2)

    class Meta:
        verbose_name = 'CampaignAnalytics'
        verbose_name_plural = 'CampaignAnalytics'


class CampaignChannel(models.Model):

    name = models.CharField(
        max_length=256, null=False, blank=False, help_text="Designates the name of the channel")

    logo = models.CharField(
        max_length=256, null=True, blank=True, help_text="Designates the logo for the channel")

    value = models.CharField(
        max_length=256, null=True, blank=True, help_text="Designates the corresponding value to a campaign channel")

    description = models.TextField(
        null=True, blank=True, help_text='Campaign channel description')

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when channel is created')

    is_deleted = models.BooleanField(default=False, help_text="Designates whether deleted or not")

    order = models.IntegerField(null=True, blank=True, help_text="Designates the order in which the campaign channel needs to be displayed")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'CampaignChannel'
        verbose_name_plural = 'CampaignChannel'


class Campaign(models.Model):

    name = models.CharField(
        max_length=256, null=False, blank=False)

    status = models.CharField(
        max_length=256, null=True, blank=True, choices=CAMPAIGN_STATUS)

    channel = models.ForeignKey(
        'CampaignChannel', null=True, blank=True, on_delete=models.SET_NULL)

    campaign_template = models.ForeignKey(
        'CampaignTemplate', null=True, blank=True, on_delete=models.CASCADE)

    campaign_template_rcs = models.ForeignKey(
        'CampaignRCSTemplate', null=True, blank=True, on_delete=models.CASCADE)

    batch = models.ForeignKey(
        'CampaignBatch', null=True, blank=True, on_delete=models.SET_NULL)

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL)

    created_date = models.DateField(default=now, db_index=True)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when campaign is created')

    start_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when campaign is sent')

    processed_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when campaign was processed completely')

    last_update_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when status is created')

    is_deleted = models.BooleanField(default=False)

    delete_datetime = models.DateTimeField(
        null=True, blank=True, help_text='datetime when campaign is deleted')

    last_saved_state = models.CharField(
        max_length=256, null=True, blank=True, choices=CAMPAIGN_LAST_SAVED_STATES)
    
    total_audience = models.IntegerField(default=0)

    is_source_dashboard = models.BooleanField(
        default=True, help_text="True when campaign sent from Dashboard GUI else False for external API")

    show_processed_datetime = models.BooleanField(default=False, help_text="True when submission date time is to be shown")

    times_campaign_tested = models.IntegerField(default=0, help_text="This field shows how many times this campaign have been tested")

    campaign_in_test = models.BooleanField(default=False, help_text="Shows if this campaign is running a test campaign")

    parent_campaign = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                        help_text="This field saves the campaign from which this campaign is scheduled")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'


class QuickReply(models.Model):
    name = models.TextField(
        null=True, blank=True, help_text='Name quick reply user clicked on')
    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bot under which this quick reply is created')
    audience_log = models.ManyToManyField(
        'CampaignAudienceLog', blank=True, help_text='Audience Log under which this quick reply is created')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'QuickReply'
        verbose_name_plural = 'QuickReplies'


class CampaignAudienceLog(models.Model):

    audience = models.ForeignKey(
        'CampaignAudience', null=True, blank=True, on_delete=models.SET_NULL)

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.CASCADE)

    recepient_id = models.CharField(
        max_length=256, null=True, blank=True, unique=True)

    request = models.TextField(
        null=True, blank=True)

    response = models.TextField(
        null=True, blank=True)

    create_datetime = models.DateTimeField(
        default=timezone.now)

    sent_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when message is sent')

    is_sent = models.BooleanField(default=False)

    is_replied = models.BooleanField(default=False, help_text='Is the message recieved is reply of campaign')

    replied_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when message is replied')

    quick_reply = models.TextField(
        null=True, blank=True, help_text='Which quick reply user clicked on')

    quick_replies = models.ManyToManyField(
        QuickReply, blank=True, help_text='New quick reply user clicked on')

    delivered_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when message is delivered')

    is_delivered = models.BooleanField(default=False, help_text="determines whether the message has been delievered for this entry or not")

    is_failed = models.BooleanField(default=False, help_text="determines whether the message has been failed for this entry or not")

    is_test = models.BooleanField(default=False, help_text="determines whether this user is used for test or not")

    read_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when message is read')

    is_read = models.BooleanField(default=False)

    is_processed = models.BooleanField(default=False, help_text="determines whether the message has been processed by our system or not")

    created_date = models.DateField(default=now, db_index=True)

    sent_date = models.DateField(default=now, db_index=True)

    delivered_date = models.DateField(default=now, db_index=True)

    read_date = models.DateField(default=now, db_index=True)

    def __str__(self):
        return self.campaign.name + " - " + self.audience.audience_id

    class Meta:
        verbose_name = 'CampaignAudienceLog'
        verbose_name_plural = 'CampaignAudienceLogs'


class CampaignAudience(models.Model):

    audience_id = models.CharField(
        max_length=256, null=False, blank=False)

    channel = models.ForeignKey(
        'CampaignChannel', null=True, blank=True, on_delete=models.SET_NULL)

    batch = models.ForeignKey(
        'CampaignBatch', null=True, blank=True, on_delete=models.SET_NULL)

    record = models.TextField(
        null=True, blank=True, help_text="All the details of audience in json format")

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL, help_text="The campaign associated with this audience model.")

    audience_unique_id = models.TextField(null=True, default='', blank=True, max_length=128, help_text="Stores unique_id of an audience in type of text as of now, this text field could be scalable to json if needed")

    def __str__(self):
        return self.audience_id

    class Meta:
        verbose_name = 'CampaignAudience'
        verbose_name_plural = 'CampaignAudience'


class CampaignBatch(models.Model):

    batch_name = models.CharField(
        max_length=256, null=False, blank=False)

    batch_header_meta = models.TextField(
        null=True, blank=True, help_text="Table header's meta detail of batch")

    sample_data = models.TextField(
        null=True, blank=True, help_text="First 3 rows of the table")

    total_audience = models.IntegerField(default=0)

    total_audience_opted = models.IntegerField(default=0)

    file_path = models.CharField(max_length=2000, null=True, blank=True)

    file_name = models.CharField(max_length=100, null=True, blank=True)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when batch is created')

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bot under which this batch is created')
    
    channel = models.ForeignKey(
        'CampaignChannel', null=True, blank=True, on_delete=models.SET_NULL, help_text='Channel under which this batch was created.')

    campaigns = models.ManyToManyField(
        'Campaign', blank=True, help_text='Campaigns in which this batch is active')

    def __str__(self):
        return self.batch_name

    class Meta:
        verbose_name = 'CampaignBatch'
        verbose_name_plural = 'CampaignBatch'


class CampaignTemplateLanguage(models.Model):

    title = models.CharField(
        max_length=256, null=False, blank=False)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when template language is created')

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'CampaignTemplateLanguage'
        verbose_name_plural = 'CampaignTemplateLanguage'


class CampaignTemplateCategory(models.Model):

    title = models.CharField(
        max_length=256, null=False, blank=False)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when template category is created')

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'CampaignTemplateCategory'
        verbose_name_plural = 'CampaignTemplateCategory'


class CampaignTemplateStatus(models.Model):

    title = models.CharField(
        max_length=256, null=False, blank=False)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when template status is created')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'CampaignTemplateStatus'
        verbose_name_plural = 'CampaignTemplateStatus'


class CampaignTemplateType(models.Model):

    title = models.CharField(
        max_length=256, null=False, blank=False)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when template type is created')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'CampaignTemplateType'
        verbose_name_plural = 'CampaignTemplateTypes'


class CampaignTemplate(models.Model):

    template_name = models.CharField(
        max_length=256, null=False, blank=False)

    template_header = models.TextField(
        null=True, blank=True, help_text="Template header format")

    template_body = models.TextField(
        null=True, blank=True, help_text="Template body format")

    template_footer = models.TextField(
        null=True, blank=True, help_text="Template footer format")

    cta_text = models.TextField(
        null=True, blank=True, help_text="Call to Actions text")

    cta_link = models.TextField(
        null=True, blank=True, help_text="Call to Actions Website Link")

    attachment_src = models.TextField(
        null=True, blank=True, help_text="Source of template attachment")
    
    template_metadata = models.TextField(
        default="{}", null=True, blank=True, help_text="Message data related to the type of template selected")

    template_type = models.ForeignKey(
        'CampaignTemplateType', null=True, blank=True, on_delete=models.SET_NULL)

    language = models.ForeignKey(
        'CampaignTemplateLanguage', null=True, blank=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(
        'CampaignTemplateCategory', null=True, blank=True, on_delete=models.SET_NULL)

    status = models.ForeignKey(
        'CampaignTemplateStatus', null=True, blank=True, on_delete=models.SET_NULL)

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bot under which this batch is created')

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when template is created')

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.template_name

    class Meta:
        verbose_name = 'CampaignTemplate'
        verbose_name_plural = 'CampaignTemplates'


class CampaignWhatsAppServiceProvider(models.Model):

    name = models.CharField(max_length=20, null=False, blank=False,
                            choices=WSP_CHOICES, help_text="Name of WhatsApp Service Provider")

    default_code_file_path = models.TextField(
        null=True, blank=True, help_text="Default code file path of the Whatsapp Service Provider")

    def __str__(self):
        # This method is defined by django itself.
        # This will return name associated with WSP_CHOICES value. (Format - get_{attribut_name}_display)
        return str(self.get_name_display())

    class Meta:
        verbose_name = 'CampaignWhatsAppServiceProvider'
        verbose_name_plural = 'CampaignWhatsAppServiceProviders'


class CampaignBotWSPConfig(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', on_delete=models.CASCADE,
                            help_text="Bot with which WSP code is configured.")

    whatsapp_service_provider = models.ForeignKey(
        CampaignWhatsAppServiceProvider, on_delete=models.CASCADE, help_text="Whatsapp service provider.")

    code = models.TextField(default="", null=True,
                            blank=True, help_text="Code of WSP.")

    namespace = models.TextField(default="", null=True,
                                 blank=True, help_text="Namespace for Whatsapp service provider")

    aws_key_id = models.TextField(default=DEFAULT_AWS_ACCESS_KEY_ID, help_text="Access key ID for AWS resource")

    aws_secret_access_key = models.TextField(default=DEFAULT_AWS_SECRET_ACCESS_KEY, help_text="Secret access key ID for accessing AWS resource")

    aws_sqs = models.TextField(default=DEFAULT_AWS_SQS, help_text="url of AWS SQS resource")

    aws_sqs_delivery_packets = models.TextField(default=DEFAULT_AWS_SQS_DELIVERY_PACKETS, help_text="url of AWS delivery SQS resource")

    enable_queuing_system = models.BooleanField(default=False, help_text="True when sqs system is enabled, else False")

    enable_delivery_queuing_system = models.BooleanField(default=False, help_text="True when delivery sqs system is enabled, else False")
    
    show_sqs_message_count = models.BooleanField(
        default=False, help_text="True when count of messages in sqs queue is to be shown, else False")

    def __str__(self):
        return str(self.bot) + " - " + str(self.whatsapp_service_provider)

    class Meta:
        verbose_name = 'CampaignBotWSPConfig'
        verbose_name_plural = 'CampaignBotWSPConfigs'


@receiver(post_save, sender=CampaignBotWSPConfig)
def set_campaign_wsp_config_object_cache(sender, instance, **kwargs):
    bot_pk = str(instance.bot.pk)
    bsp_name = str(instance.whatsapp_service_provider.name)
    cache.set("CAMPAIGN_BOT_WSP_CONFIG_OBJ_" + bot_pk +
              '_' + bsp_name, instance, settings.CACHE_TIME)


class CampaignAPI(models.Model):

    api_program = models.TextField(
        default=API_INTEGRATION_SAMPLE_CODE_RML, null=True, blank=True, help_text="Python's code for api")

    campaign_bot_wsp_config = models.ForeignKey(
        CampaignBotWSPConfig, on_delete=models.SET_NULL, null=True, blank=True, help_text="Bot WSP config associated with campaign.")

    is_api_completed = models.BooleanField(default=True)

    api_complete_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when api development is completed')

    last_update_datetime = models.DateTimeField(
        default=timezone.now, help_text='Last datetime when api is edited')

    is_being_edited = models.BooleanField(default=False)

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.campaign.name

    class Meta:
        verbose_name = 'CampaignAPI'
        verbose_name_plural = 'CampaignAPI'


class CampaignAuthUser(models.Model):

    user = models.ForeignKey(User, null=True, blank=True,
                             on_delete=models.SET_NULL, help_text="Logged in User")

    email_id = models.CharField(
        max_length=256, null=False, blank=False)

    otp = models.CharField(max_length=200)

    expire_datetime = models.DateTimeField(
        default=None, blank=True, null=True)

    otp_sent_count = models.IntegerField(default=0)

    last_otp_sent_time = models.DateTimeField(
        default=timezone.now, help_text='First datetime when otp is sent to the particular user id')

    is_otp_expired = models.BooleanField(default=True)

    access_token = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text='unique access token key to access api editor')

    is_token_expired = models.BooleanField(default=True)

    def __str__(self):
        return self.email_id

    class Meta:
        verbose_name = 'CampaignAuthUser'
        verbose_name_plural = 'CampaignAuthUser'


class CampaignAPILogger(models.Model):

    user = models.ForeignKey(
        'CampaignAuthUser', null=True, blank=True, on_delete=models.SET_NULL)

    api_program = models.TextField(
        null=True, blank=True, help_text="Python's code for api")

    update_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime when code is being edited')

    campaign_api = models.ForeignKey(
        'CampaignAPI', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email_id

    class Meta:
        verbose_name = 'CampaignAPILogger'
        verbose_name_plural = 'CampaignAPILogger'


class CampaignFileAccessManagement(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique access token key')

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    is_public = models.BooleanField(default=False)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True, help_text="Original name of file without adding any marker to make it unique")

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL, help_text="It holds the reference to the bot with which it is associated")

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.is_public)

    class Meta:
        verbose_name = 'CampaignFileAccessManagement'
        verbose_name_plural = 'CampaignFileAccessManagement'


class CampaignConfig(models.Model):
    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL)

    session_time = models.IntegerField(
        default=4, help_text="Session time for API Integration (in hours)")

    system_commands = models.TextField(
        null=True, default="['os.system', 'subprocess', 'import threading', 'threading.Thread', 'ssh']")

    caller_ids = models.ManyToManyField('VoiceBotCallerID', blank=True, help_text='All caller ids available for this bot')
    
    def __str__(self):
        if self.bot:
            return self.bot.name
        
    class Meta:
        verbose_name = 'CampaignConfig'
        verbose_name_plural = 'CampaignConfig'


class CampaignExportRequest(models.Model):
    email_id = models.CharField(
        max_length=500, null=False, blank=False, help_text='Email address to send report')

    export_type = models.CharField(
        max_length=256, null=True, blank=True, choices=EXPORT_CHOICES)

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL, help_text='Campaign to be exported if export type is single export')

    start_date = models.DateTimeField(default=timezone.now)

    end_date = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE)

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=False, on_delete=models.SET_NULL)

    is_completed = models.BooleanField(default=False, null=False, blank=False)

    masking_enabled = models.BooleanField(
        default=False, help_text="Designates whether masking PII data is enabled or not")

    filters_on_export = models.TextField(
        null=True, default="{}", help_text='On which variable export should be done')

    def __str__(self):
        return self.email_id

    class Meta:
        verbose_name = 'CampaignExportRequest'
        verbose_name_plural = 'CampaignExportRequests'


class CampaignTemplateVariable(models.Model):
    variables = models.TextField(
        null=True, default="[]", help_text='User details which will be used to replace the variables in template')

    total_variables = models.IntegerField(
        default=0, help_text="Total number of variables present in this template")
    
    dynamic_cta_url_variable = models.TextField(
        null=True, default="[]", help_text='User details which will be used to replace the URL variables in template')
    
    header_variable = models.TextField(
        null=True, default="[]", help_text='User details which will be used to replace the header variables in template')

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=False, on_delete=models.SET_NULL)

    batch = models.ForeignKey(
        'CampaignBatch', null=True, blank=False, on_delete=models.SET_NULL)

    template = models.ForeignKey(
        'CampaignTemplate', null=True, blank=False, on_delete=models.SET_NULL)

    attachment_details = models.TextField(
        null=True, default=dict(), help_text='It will store custom attachment details of user')
    
    def __str__(self):
        if self.campaign and self.batch and self.template:
            return self.campaign.name + ' - ' + self.batch.batch_name + ' - ' + self.template.template_name
        else:
            return '-'

    class Meta:
        verbose_name = 'CampaignTemplateVariable'
        verbose_name_plural = 'CampaignTemplateVariables'


class CampaignAuthToken(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique access token key')

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=False, on_delete=models.SET_NULL)

    user = models.ForeignKey(
        'EasyChatApp.User', null=True, blank=False, on_delete=models.CASCADE)

    is_expired = models.BooleanField(default=False, null=False, blank=False)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when campaign token is created.")

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'CampaignAuthToken'
        verbose_name_plural = 'CampaignAuthTokens'


class CampaignSchedule(models.Model):

    choices = models.CharField(
        max_length=256, null=True, choices=SCHEDULE_CHOICES, default=SCHEDULE_CHOICES[0][0])

    days = models.CharField(max_length=500, default="[]")

    metadata = models.TextField(default="[]", null=False, blank=False)

    start_date = models.DateField(
        default=now, help_text="Date when schedule will be created")

    end_date = models.DateField(
        null=True, blank=True, help_text="Date when schedule will be ended")

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=False, on_delete=models.CASCADE)

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.CASCADE)

    updated_upto = models.DateField(
        null=True, blank=True, help_text="Date upto which schedules are created")

    created_at = models.DateTimeField(
        default=timezone.now, help_text="Date and time on which schedule is created")

    def __str__(self):
        return str(self.bot) + '-' + str(self.campaign) + '-' + str(self.pk)

    class Meta:
        verbose_name = 'CampaignSchedule'
        verbose_name_plural = 'CampaignSchedules'


class CampaignScheduleObject(models.Model):

    campaign_schedule = models.ForeignKey(
        'CampaignSchedule', null=True, blank=False, on_delete=models.CASCADE)

    date = models.DateField(null=True, blank=True,
                            help_text="Date when this object will be executed")

    time = models.TimeField(null=True, blank=True,
                            help_text="Time when this object will be executed")

    uid = models.UUIDField(
        default=uuid.uuid4, editable=True, help_text='unique access id per time slot')

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=False, on_delete=models.CASCADE)

    is_sent = models.BooleanField(
        default=False, help_text="boolean to check whether campaign has been triggered or not")

    channel = models.ForeignKey(
        'CampaignChannel', null=True, blank=True, on_delete=models.SET_NULL)

    campaign_batch = models.ForeignKey(CampaignBatch, null=True, blank=False, on_delete=models.CASCADE,
                                       help_text="The batch file which to be used for this schedule")

    edited_on = models.DateTimeField(
        null=True, blank=True, help_text="Date and Time when this schdule is modified")

    def __str__(self):
        return str(self.campaign_schedule) + '-' + str(self.date) + '-' + str(self.time)

    class Meta:
        verbose_name = 'CampaignScheduleObject'
        verbose_name_plural = 'CampaignScheduleObjects'


@receiver(post_save, sender=CampaignScheduleObject)
def update_updated_upto_attribute(sender, instance, **kwargs):
    if kwargs["created"] and not kwargs["raw"]:
        campaign_schedule = instance.campaign_schedule
        if campaign_schedule.updated_upto != None:
            if campaign_schedule.updated_upto < instance.date:
                campaign_schedule.updated_upto = instance.date
                campaign_schedule.save()
        else:
            campaign_schedule.updated_upto = instance.date
            campaign_schedule.save()


class CampaignVoiceBotSetting (models.Model):

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=False, on_delete=models.CASCADE)

    caller_id = models.CharField(
        max_length=20, blank=True, help_text="Number from which call will be initiated")

    app_id = models.CharField(max_length=500, blank=True,
                              help_text="Determines which flow to execute during call")

    campaign_sid = models.CharField(
        max_length=500, default="", help_text='Campaign ID provided by exotel')

    url = models.CharField(max_length=500, default="", help_text='applet URL')

    start_date = models.DateField(
        default=now, help_text="Date when campaign will start")

    start_time = models.TimeField(
        null=True, blank=True, help_text="Time when campaign will start")

    end_date = models.DateField(
        default=now, help_text="Date when campaign will end")

    end_time = models.TimeField(
        null=True, blank=True, help_text="Time when campaign will end")

    retry_setting = models.ForeignKey(
        'VoiceBotRetrySetting', null=True, blank=False, on_delete=models.CASCADE)

    request = models.TextField(default="", null=True, blank=True,
                               help_text="Request params when calling create campaign API")

    response = models.TextField(default="", null=True, blank=True,
                                help_text="Response received from create campaign API")

    is_saved = models.BooleanField(
        default=False, null=False, blank=False, help_text="Indicates whether setting is saved or not")

    is_details_fetched = models.BooleanField(default=False, help_text="This designates whether the call details are fetched or not.")

    def __str__(self):
        return str(self.campaign) + '-' + str(self.start_date) + '-' + str(self.end_date)

    class Meta:
        verbose_name = 'CampaignVoiceBotSetting'
        verbose_name_plural = 'CampaignVoiceBotSettings'


class VoiceBotRetrySetting (models.Model):

    mechanism = models.CharField(
        max_length=256, null=True, choices=RETRY_MECHANISM, default=RETRY_MECHANISM[0][0])

    no_of_retries = models.IntegerField(default=1)

    retry_interval = models.IntegerField(default=2)

    is_busy_enabled = models.BooleanField(
        default=True, null=False, blank=False, help_text="Indicates whether retry on status 'busy' is enabled or not")

    is_no_answer_enabled = models.BooleanField(
        default=True, null=False, blank=False, help_text="Indicates whether retry on status 'no answer' is enabled or not")

    is_failed_enabled = models.BooleanField(
        default=True, null=False, blank=False, help_text="Indicates whether retry on status 'failed' is enabled or not")

    def __str__(self):
        return str(self.mechanism)

    class Meta:
        verbose_name = 'VoiceBotRetrySetting'
        verbose_name_plural = 'VoiceBotRetrySettings'


class CampaignVoiceBotAPI (models.Model):

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=False, on_delete=models.CASCADE)

    api_code = models.TextField(
        default=VOICE_BOT_SAMPLE_API_CODE, null=False, blank=False, help_text="Write Voice Bot API code here.")

    def __str__(self):
        return str(self.campaign)

    class Meta:
        verbose_name = 'CampaignVoiceBotAPI'
        verbose_name_plural = 'CampaignVoiceBotAPI'


class VoiceBotCallerID (models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True, blank=True, on_delete=models.SET_NULL, help_text="It represents with which bot this caller id is associated.")

    caller_id = models.CharField(
        max_length=20, blank=True, help_text="Number from which call will be initiated")

    app_id = models.CharField(max_length=100, blank=True,
                              help_text="Determines which flow to execute during call")

    def __str__(self):
        return f"{self.caller_id} - {self.app_id}"

    class Meta:
        verbose_name = 'VoiceBotCallerID'
        verbose_name_plural = 'VoiceBotCallerID'


class CampaignVoiceBotAnalytics(models.Model):

    total_audience = models.IntegerField(default=0, null=True, blank=True)

    call_scheduled = models.IntegerField(default=0, null=True, blank=True)

    call_initiated = models.IntegerField(default=0, null=True, blank=True)

    call_completed = models.IntegerField(default=0, null=True, blank=True)

    call_failed = models.IntegerField(default=0, null=True, blank=True)

    call_in_progress = models.IntegerField(default=0, null=True, blank=True)

    call_invalid = models.IntegerField(default=0, null=True, blank=True)

    call_failed_dnd = models.IntegerField(default=0, null=True, blank=True)

    call_retry = models.IntegerField(default=0, null=True, blank=True)

    call_retrying = models.IntegerField(default=0, null=True, blank=True)

    call_created = models.IntegerField(default=0, null=True, blank=True)

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.campaign.name + " - " + str(self.total_audience)

    class Meta:
        verbose_name = 'CampaignVoiceBotAnalytics'
        verbose_name_plural = 'CampaignVoiceBotAnalytics'


class CampaignVoiceBotDetailedAnalytics(models.Model):

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.CASCADE)

    from_number = models.CharField(
        max_length=20, blank=True, help_text="Number to which call was initiated")

    to_number = models.CharField(
        max_length=20, blank=True, help_text="Number from which call was initiated")

    call_sid = models.CharField(
        max_length=500, default="", help_text='Call ID provided by exotel')

    status = models.CharField(
        max_length=20, blank=True, help_text="Number to which call was initiated")

    date_created = models.DateTimeField(
        default=timezone.now, help_text='datetime when call was created')

    date_updated = models.DateTimeField(
        default=timezone.now, help_text='datetime when call was updated')

    direction = models.CharField(
        max_length=20, blank=True, help_text="Call direction")

    call_start_time = models.DateTimeField(
        default=timezone.now, help_text='datetime when call was started')

    total_duration = models.IntegerField(default=0, null=True, blank=True)

    on_call_duration = models.IntegerField(default=0, null=True, blank=True)

    price = models.FloatField(default=0.0, null=True, blank=True)

    is_details_fetched = models.BooleanField(
        default=False, null=False, blank=False, help_text="Indicates whether call details were fetched from API or not")

    audience_unique_id = models.TextField(null=True, default='', blank=True, max_length=128, help_text="Stores unique_id of an audience in type of text as of now, this text field could be scalable to json if needed")

    def __str__(self):
        if self.campaign:
            return self.campaign.name + " - " + str(self.from_number)
        else:
            return "None - " + str(self.from_number)

    class Meta:
        verbose_name = 'CampaignVoiceBotDetailedAnalytics'
        verbose_name_plural = 'CampaignVoiceBotDetailedAnalytics'


class CampaignRCSDetailedAnalytics(models.Model):

    campaign = models.ForeignKey(
        'Campaign', null=True, blank=True, on_delete=models.SET_NULL)

    submitted = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of mobile numbers submitted")

    sent = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of sent messages")

    delivered = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of delivered messages")

    read = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of read messages")

    failed = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of failed messages")

    replied = models.IntegerField(
        default=0, null=True, blank=True, help_text="Total number of replied messages")

    template = models.ForeignKey(
        'CampaignRCSTemplate', null=True, blank=True, on_delete=models.SET_NULL)

    message_type = models.CharField(
        max_length=20, blank=True, help_text="Type of message sent")

    start_time = models.DateTimeField(
        default=timezone.now, help_text='Start time of the RCS Campaign')

    end_time = models.DateTimeField(
        default=timezone.now, help_text='End time of the RCS Campaign')

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bot under which this campaign is created')

    def __str__(self):
        return self.campaign.name

    class Meta:
        verbose_name = 'CampaignRCSDetailedAnalytics'
        verbose_name_plural = 'CampaignRCSDetailedAnalytics'


class CampaignRCSTemplate(models.Model):

    template_name = models.CharField(
        max_length=256, null=False, blank=False, help_text="Name of RCS Message Template")

    message_type = models.CharField(
        max_length=256, null=True, blank=True, choices=RCS_MESSAGE_TEMPLATE_CHOICES, help_text="Type of RCS message template selected")

    template_metadata = models.TextField(
        default="{}", null=True, blank=True, help_text="Message data related to the type of template selected")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='Timestamp when template is created')

    bot = models.ForeignKey(
        'EasyChatApp.bot', null=True, blank=True, on_delete=models.SET_NULL, help_text='Bot under which this Template is created')

    is_deleted = models.BooleanField(
        default=False, help_text="Denotes whether the template is deleted")

    def __str__(self):
        return self.template_name

    class Meta:
        verbose_name = 'CampaignRCSTemplate'
        verbose_name_plural = 'CampaignRCSTemplates'


class CampaignCronjobTracker(models.Model):

    function_id = models.CharField(
        max_length=100, null=False, help_text="Function id of a cronjob function which is running")

    creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the cronjob tracker object was created')
    
    class Meta:
        verbose_name = "CampaignCronjobTracker"
        verbose_name_plural = "CampaignCronjobTrackers"

    def __str__(self):
        return self.function_id
    
        '''
    This function is used only for checking whether the object created for 
    the schedular has expired or not. It is not used in the case of cronjobs.
    '''
    
    def is_object_expired(self, expiration_time):
        try:
            expiry_time_limit_in_seconds = expiration_time * 60
            total_time_elapsed = int((timezone.now() - self.creation_datetime).total_seconds())
            if total_time_elapsed >= expiry_time_limit_in_seconds:
                return True

            return False
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in CampaignCronjobTracker is_object_expired method %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp'})
            return False


class CampaignEventProgress (models.Model):
    event_id = models.UUIDField(
        default=uuid.uuid4, editable=False)

    event_type = models.CharField(max_length=256,
                                  null=False,
                                  blank=False,
                                  choices=CAMPAIGN_EVENT_CHOICES,
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

    def __str__(self):
        try:
            return f'{str(self.event_type)} -- {str(self.event_progress)} -- {str(self.bot.name)}'
        except Exception:
            return 'Event'

    class Meta:
        verbose_name = "CampaignEventProgress"
        verbose_name_plural = "CampaignEventProgress"


class CampaignVoiceUser(models.Model):

    mobile_number = models.CharField(max_length=10, help_text="This field is used to store the mobile number of the user.")

    voice_campaign = models.ForeignKey(CampaignVoiceBotSetting, null=True, blank=True, on_delete=models.CASCADE, help_text="It is used to store the relation with campaign.")

    voice_bot_profile = models.ForeignKey('EasyChatApp.VoiceBotProfileDetail', null=True, blank=True, on_delete=models.SET_NULL, help_text="It is used to store the campaign session details.")

    status = models.CharField(max_length=15, choices=VOICE_CAMPAIGN_CALL_STATUS, null=True, blank=True, help_text="It designates status of the call.")

    duration = models.CharField(max_length=10, null=True, blank=True, help_text="This designates the duration of call.")

    date = models.DateField(null=True, blank=True, help_text="It is the date at which call was initiated.")

    time = models.TimeField(null=True, blank=True, help_text="It is the time at which call was initiated.")

    call_sid = models.CharField(max_length=500, default="", help_text='Call ID provided by exotel')

    on_call_duration = models.IntegerField(default=0, null=True, blank=True, help_text="On call duration")

    price = models.FloatField(default=0.0, null=True, blank=True, help_text="Price of call provided by exotel")

    def __str__(self):
        try:
            return f'{str(self.mobile_number)} -- {str(self.voice_campaign.campaign.name)}'
        except Exception:
            return self.pk

    def get_created_date_time(self):
        try:
            if self.date and self.time:
                return self.date.strftime("%d/%m/%Y") + ", " + self.time.strftime("%H:%M %p")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_created_date_time: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    def get_call_duration(self):
        try:
            if self.duration:
                return self.duration + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_call_duration: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    def get_call_status(self):
        try:
            if self.status:
                return self.get_status_display()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_call_status: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    def get_call_recording(self):
        try:
            if self.voice_bot_profile:
                return json.loads(self.voice_bot_profile.end_event_meta_data)["requestMetadata"]["RecordingUrl"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_call_recording: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    def get_voice_user_id(self):
        try:
            if self.voice_bot_profile:
                return str(self.voice_bot_profile.profile.user_id)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_voice_user_id: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    def get_dispostion_code_data(self):
        try:
            disposition_code = "N/A"
            if self.voice_bot_profile:
                if self.voice_bot_profile.profile.tree:
                    disposition_code = self.voice_bot_profile.profile.tree.disposition_code
                    if not disposition_code:
                        disposition_code = self.voice_bot_profile.profile.tree.name

                    intent_obj = get_intent_obj_from_tree_obj(self.voice_bot_profile.profile.tree)
                    
                    parent_tree = get_parent_tree_obj(self.voice_bot_profile.profile.tree)
                    parent_tree_pk = "-1"
                    if parent_tree:
                        parent_tree_pk = str(parent_tree.pk)

                    if not intent_obj:
                        return "None", "", "", ""
                    
                    return disposition_code, str(intent_obj.pk), str(self.voice_bot_profile.profile.tree.pk), parent_tree_pk
                else:
                    return "None", "", "", ""
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_dispostion_code_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        
        return "N/A", "", "", ""

    def get_call_sid(self):
        try:
            if self.call_sid:
                return str(self.call_sid)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_call_sid: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "N/A"

    class Meta:
        verbose_name = "CampaignVoiceUser"
        verbose_name_plural = "CampaignVoiceUsers"


class VoiceCampaignHistoryExportRequest(models.Model):

    user = models.ForeignKey('EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE, help_text="Easychat user who requested for data")

    request_data = models.TextField(null=True, blank=True, help_text="The request packet of export data reuired.")

    is_completed = models.BooleanField(default=False, help_text="This designates whether the request is served or not.")

    date_created = models.DateField(default=now, null=True, blank=True, help_text="It is the date on which the data was requested.")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "VoiceCampaignHistoryExportRequest"
        verbose_name_plural = "VoiceCampaignHistoryExportRequests"


class CampaignHistoryExportRequest(models.Model):

    user = models.ForeignKey('EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE, help_text="Easychat user who requested for data")

    request_data = models.TextField(null=True, blank=True, help_text="The request packet of export data required.")

    is_completed = models.BooleanField(default=False, help_text="This designates whether the request is served or not.")

    date_created = models.DateField(default=now, null=True, blank=True, help_text="It is the date on which the data was requested.")

    is_whatsapp = models.BooleanField(default=False, help_text="This indicates of WhatsappCampaign export.")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "CampaignHistoryExportRequest"
        verbose_name_plural = "CampaignHistoryExportRequests"
