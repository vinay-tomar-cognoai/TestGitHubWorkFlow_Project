from django.db import models
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.functions import Length
from EasyAssistApp.constants import *
from EasyAssistApp.encrypt import CustomEncrypt
from EasyAssistApp.utils import generate_random_password, create_static_files_access_token_specific,\
    save_system_audit_trail, send_page_refresh_request_to_agent, \
    get_hashed_data, get_masked_data_if_hashed, hash_crucial_info_in_data, CRMDocumentGenerator, \
    get_time_in_hours_mins_secs, update_virtual_agent_code

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


class CobrowseAgent(models.Model):

    user = models.OneToOneField(
        "EasyChatApp.User", on_delete=models.CASCADE, primary_key=True)

    role = models.CharField(max_length=256,
                            null=False,
                            blank=False,
                            choices=USER_CHOICES)

    support_level = models.CharField(
        max_length=3, choices=COBROWSING_AGENT_SUPPORT, default="L1", null=False, blank=False)

    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    location = models.CharField(
        max_length=100, null=True, blank=True)

    agent_creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the agents account was created')

    agents = models.ManyToManyField('CobrowseAgent', blank=True)

    is_active = models.BooleanField(default=False)

    is_account_active = models.BooleanField(default=True)

    is_switch_allowed = models.BooleanField(default=False)

    show_static_analytics = models.BooleanField(default=False)

    options = models.TextField(null=True, blank=True)

    agent_code = models.CharField(max_length=256, null=True, blank=True)

    last_agent_active_datetime = models.DateTimeField(
        null=True, blank=True, default=timezone.now, help_text='datetime when last update from agent for active')
    
    agent_activation_datetime = models.DateTimeField(
        null=True, blank=True, help_text='last activation datetime of agent')

    agent_deactivation_datetime = models.DateTimeField(
        null=True, blank=True, help_text='last deactivation datetime of agent')
    
    is_cobrowsing_active = models.BooleanField(
        default=False, help_text='Currently active in cobrowsing session')

    supported_language = models.ManyToManyField('LanguageSupport', blank=True)

    product_category = models.ManyToManyField('ProductCategory', blank=True)

    is_cognomeet_active = models.BooleanField(
        default=False, help_text='Currently active in meetings session')

    virtual_agent_code = models.CharField(
        max_length=100, null=True, blank=True, unique=True)

    last_lead_assigned_datetime = models.DateTimeField(
        null=True, blank=True, help_text='Datetime when last Cobrowsing request was assigned to the agent')

    resend_password_count = models.IntegerField(
        default=RESEND_PASSWORD_THRESHOLD, help_text='Number of times resend password has been initiated in a day')

    last_password_resend_date = models.DateField(
        default=timezone.now, help_text='Date when last time resend password was initiated')

    last_active_in_meet_datetime = models.DateTimeField(
        null=True, blank=True, default=timezone.now, help_text='datetime when last update from agent for active in meet')

    assign_followup_leads = models.BooleanField(
        default=True, help_text='If true, this agent will be assigned follow up leads')

    agent_profile_pic_source = models.CharField(
        max_length=500, blank=True, default="", help_text='source of agent profile picture')

    total_agents_created = models.IntegerField(
        default=0, null=True, blank=True, help_text='Number of agents created')

    total_supervisors_created = models.IntegerField(
        default=0, null=True, blank=True, help_text='Number of supervisors created')

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    def get_easychat_version(self):
        easychat_version = ""
        try:
            easychat_version = settings.EASYCHAT_VERSION
            return easychat_version
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_easychat_version %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def name(self):
        return self.user.username

    def agent_name(self):
        try:
            first_name = self.user.first_name
            if(first_name != None and len(first_name) > 0):
                return first_name
            else:
                return self.name()
        except Exception:
            logger.warning("Error while fetching Agent's name", extra={
                'AppName': 'EasyAssist'})
            return ""

    def save(self, *args, **kwargs):

        if self.user.username != None and self.user.username.endswith("@getcogno.ai"):
            self.is_switch_allowed = True

        if self.agent_code == None or self.agent_code == "":
            self.agent_code = self.user.username

        if self.virtual_agent_code == None or self.virtual_agent_code == "":
            try:
                hashed_username = hashlib.md5(
                    self.user.username.encode()).hexdigest()
                hashed_username = hashed_username[:6] + str(self.pk)
                if len(hashed_username) > 7:
                    hashed_username = hashed_username[-7:]
                self.virtual_agent_code = hashed_username
            except Exception:
                logger.warning("Error in auto generated virtual agent code", extra={
                               'AppName': 'EasyAssist'})

        super(CobrowseAgent, self).save(*args, **kwargs)

    def __str__(self):
        return self.name()

    def get_access_token_obj(self):
        try:
            if self.access_token:
                return self.access_token

            if self.role == "admin":
                return CobrowseAccessToken.objects.get(agent=self)
            elif self.role == "supervisor":
                # supervisor mapped under admin 
                admin_agent = CobrowseAgent.objects.filter(agents__pk=self.pk).exclude(role="admin_ally").first()
                # if we get none above then supervisor is mapped under admin ally
                if not admin_agent:
                    # getting admin ally
                    admin_ally_obj = CobrowseAgent.objects.filter(agents__pk=self.pk).first()
                    if admin_ally_obj:
                        admin_agent = CobrowseAgent.objects.filter(agents__pk=admin_ally_obj.pk).first()

                return CobrowseAccessToken.objects.filter(agent=admin_agent).first()
            elif self.role == "admin_ally":
                return CobrowseAccessToken.objects.get(agent=CobrowseAgent.objects.filter(agents__pk=self.pk).exclude(role="admin_ally")[0])
            else:
                parent_user = self
                try:
                    parent_user = CobrowseAgent.objects.filter(
                        agents__pk=self.pk).exclude(Q(pk=self.pk) | Q(role="admin_ally"))[0]
                    try:
                        second_parent = CobrowseAgent.objects.filter(
                            agents__pk=parent_user.pk).exclude(Q(pk=parent_user.pk) | Q(role="admin_ally"))[0]
                        return CobrowseAccessToken.objects.get(agent=second_parent)
                    except Exception:
                        return CobrowseAccessToken.objects.get(agent=parent_user)
                except Exception:
                    return CobrowseAccessToken.objects.get(agent=self)
        except Exception:
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # logger.error("Error get_access_token_obj %s at %s", str(
            #     e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def is_agent_active(self):
        try:
            if self.get_access_token_obj().disable_auto_offline_agent == True:
                return self.is_active

            total_sec = int(
                (timezone.now() - self.last_agent_active_datetime).total_seconds())
            if total_sec > 30:
                self.is_active = False
                self.save()
                return False
            else:
                return True
        except Exception:
            return False

    def is_agent_in_meeting(self):
        try:
            total_sec = int(
                (timezone.now() - self.last_active_in_meet_datetime).total_seconds())
            if self.is_cognomeet_active == False:
                return False
            if total_sec > 60:
                self.is_cognomeet_active = False
                self.save()
                return False
            else:
                return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_agent_in_meeting %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def get_supported_languages(self):
        supported_language = ""
        try:
            supported_language_objs = self.supported_language.filter(
                is_deleted=False).order_by('index')
            supported_language = ", ".join(
                [supported_language.title for supported_language in supported_language_objs])
            return supported_language
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_supported_languages %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_product_categories(self):
        product_category = ""
        try:
            product_category_objs = self.product_category.filter(
                is_deleted=False).order_by('index')
            product_category = ", ".join(
                [product_category.title for product_category in product_category_objs])
            return product_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_product_categories %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_supported_languages_limited(self):
        try:
            max_length = 15
            supported_language_objs = self.supported_language.filter(
                is_deleted=False).order_by('index')
            supported_language_all = ", ".join(
                [supported_language.title for supported_language in supported_language_objs])
            supported_language_all = supported_language_all.strip()

            supported_language = supported_language_all[:max_length]
            if supported_language.rfind(",") > 0:
                supported_language = supported_language[: supported_language.rfind(
                    ",")]

            if len(supported_language_all) > len(supported_language):
                return supported_language + ", ..."
            else:
                return supported_language
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_supported_languages_limited %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_product_categories_limited(self):
        try:
            max_length = 15
            product_category_objs = self.product_category.filter(
                is_deleted=False).order_by('index')
            product_category_all = ", ".join(
                [product_category.title for product_category in product_category_objs])
            product_category_all = product_category_all.strip()

            product_category = product_category_all[:max_length]
            if product_category.rfind(",") > 0:
                product_category = product_category[: product_category.rfind(
                    ",")]

            if len(product_category_all) > len(product_category):
                return product_category + ", ..."
            else:
                return product_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_product_categories_limited %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def is_cognoai_user(self):
        try:
            if self.user and self.user.username.endswith("@getcogno.ai"):
                return True

            return False
        except Exception:
            return False

    def get_supervisors(self):
        try:
            supervisors_list = ""
            supervisors = CobrowseAgent.objects.filter(agents=self)
            supervisors_list = ", ".join(
                [supervisor.name() for supervisor in supervisors])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_supervisors %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return supervisors_list

    def is_agent_creation_limit_exhausted(self):
        try:
            access_token_obj = self.get_access_token_obj()
            supervisor_agent_creation_limit = access_token_obj.supervisor_agent_creation_limit
            adminally_agent_creation_limit = access_token_obj.adminally_agent_creation_limit
            if self.role == "supervisor" and supervisor_agent_creation_limit != None and self.total_agents_created >= supervisor_agent_creation_limit:
                return True
            if self.role == "admin_ally" and adminally_agent_creation_limit != None and self.total_agents_created >= adminally_agent_creation_limit:
                return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_agent_creation_limit_exhausted %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return False

    def is_supervisor_creation_limit_exhausted(self):
        try:
            access_token_obj = self.get_access_token_obj()
            adminally_supervisor_creation_limit = access_token_obj.adminally_supervisor_creation_limit
            if self.role == "admin_ally" and adminally_supervisor_creation_limit != None and self.total_supervisors_created >= adminally_supervisor_creation_limit:
                return True

            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_supervisor_creation_limit_exhausted %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return False
    
    def agent_full_name(self):
        agent_name = "-"
        try:
            first_name = self.user.first_name
            if first_name:
                agent_name = first_name + " " + self.user.last_name
        except Exception:
            logger.warning("Error while fetching Agent's full name", extra={
                'AppName': 'EasyAssist'})
        return agent_name

    class Meta:
        verbose_name = "CobrowseAgent"
        verbose_name_plural = "CobrowseAgent"


@receiver(post_save, sender=CobrowseAgent)
def create_cobrowse_access_token(sender, instance, **kwargs):
    if instance.role == "admin" and not kwargs["raw"]:
        if CobrowseAccessToken.objects.filter(agent=instance).count() == 0:
            username = hashlib.md5(instance.user.username.encode()).hexdigest()
            password = generate_random_password()
            access_token = CobrowseAccessToken.objects.create(
                agent=instance, client_id=username, client_key=password)
            instance.access_token = access_token
            instance.save()

        default_language_support = instance.supported_language.filter(
            title="English").first()

        if default_language_support == None:
            default_language_support = LanguageSupport.objects.create(
                title="English")

        default_language_support.is_deleted = False
        default_language_support.save()

        instance.supported_language.add(default_language_support)


class AgentPasswordHistory(models.Model):

    agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                              on_delete=models.CASCADE, help_text='Agent')

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when password is saved')

    password_hash = models.TextField(help_text="password hash")

    def __str__(self):
        return self.agent.user.username

    class Meta:
        verbose_name = 'AgentPasswordHistory'
        verbose_name_plural = 'AgentPasswordHistory'


class CobrowseIO(models.Model):

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique session id for each cobrowsing session')

    title = models.CharField(max_length=1000, null=True, blank=True,
                             help_text='title of webpage from which request has been generated')

    active_url = models.CharField(max_length=1000, null=True, blank=True,
                                  help_text='active webpage url where client is filling the form', db_index=True)

    html = models.TextField(null=True, blank=True,
                            help_text='html content of webpage')

    is_updated = models.BooleanField(
        default=True, help_text='bool: html is updated or not')

    position = models.TextField(
        null=True, blank=True, help_text='highlight element position')

    is_highlighted = models.BooleanField(
        default=False, help_text='bool: position is updated or not')

    full_name = models.CharField(max_length=100, help_text='client full name')

    mobile_number = models.CharField(
        max_length=100, help_text='client mobile number')

    latitude = models.CharField(
        max_length=100, null=True, blank=True, default=None)

    longitude = models.CharField(
        max_length=100, null=True, blank=True, default=None)

    request_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when lead is generated')

    is_active = models.BooleanField(
        default=False, help_text='bool: client is active or not')

    meta_data = models.TextField(
        null=True, blank=True, help_text='meta data container')

    drop_off_meta_data = models.TextField(
        null=True, blank=True, help_text='drop off meta data container')

    last_update_datetime = models.DateTimeField(
        null=True, blank=True, help_text='datetime when last update from client has been received')

    is_archived = models.BooleanField(
        default=False, help_text='bool: lead is archived or not', db_index=True)

    agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                              on_delete=models.SET_NULL, help_text='agent assigned to client for cobrowsing')

    is_agent_connected = models.BooleanField(
        default=True, help_text='bool: agent is connected or not')

    take_screenshot = models.BooleanField(
        default=False, help_text='bool: take screenshot or client screen')

    master_type_screenshot_list = (("screenshot", "screenshot"),
                                   ("pageshot", "pageshot"))

    type_screenshot = models.CharField(
        choices=master_type_screenshot_list, max_length=20, null=True, blank=True, help_text='type of screenshot')

    last_agent_update_datetime = models.DateTimeField(
        null=True, blank=True, help_text='datetime when last update from agent has been received')

    agent_comments = models.TextField(
        null=True, blank=True, help_text='Closing remarks added by agent on closing session')

    is_lead = models.BooleanField(default=False)

    primary_value = models.CharField(max_length=1000, null=True, blank=True)

    agent_assistant_request_status = models.BooleanField(default=False)

    is_agent_request_for_cobrowsing = models.BooleanField(
        default=False, help_text="This flag indicates if the agent asked for cobrowsing or meeting.")

    is_customer_request_for_cobrowsing = models.BooleanField(
        default=False, help_text="This flag indicates if the customer asked for cobrowsing or meeting.")

    agent_meeting_request_status = models.BooleanField(default=False)

    customer_meeting_request_status = models.BooleanField(default=False)

    master_allow_agent_cobrowse = (("true", "true"),
                                   ("false", "false"))

    allow_agent_cobrowse = models.CharField(
        choices=master_allow_agent_cobrowse, null=True, blank=True, max_length=10)

    allow_agent_meeting = models.CharField(
        choices=master_allow_agent_cobrowse, null=True, blank=True, max_length=10)

    allow_customer_meeting = models.CharField(
        choices=master_allow_agent_cobrowse, null=True, blank=True, max_length=10)

    client_comments = models.TextField(
        null=True, blank=True, help_text='Feedback given by client on session close event')

    agent_rating = models.IntegerField(
        null=True, blank=True, help_text='NPS rating given by client to agent')

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    consent_allow_count = models.IntegerField(default=0)

    consent_cancel_count = models.IntegerField(default=0)

    otp_validation = models.CharField(max_length=4, null=True, blank=True)

    request_meta_details = models.TextField(null=True, blank=True)

    support_agents = models.ManyToManyField(
        CobrowseAgent, blank=True, related_name="support_agents")

    is_closed_session = models.BooleanField(default=False)

    init_transaction = models.BooleanField(default=False)

    init_transaction_datetime = models.DateTimeField(default=timezone.now)

    cobrowsing_start_datetime = models.DateTimeField(
        default=None, null=True, blank=True)

    meeting_start_datetime = models.DateTimeField(
        default=None, null=True, blank=True)

    share_client_session = models.BooleanField(
        default=False, help_text="If this is true then session is shared with client")

    is_helpful = models.BooleanField(
        default=False, help_text='Session was helpful and lead closed successfully.')

    is_test = models.BooleanField(
        default=False, help_text='Session was for testing')

    is_reverse_cobrowsing = models.BooleanField(
        default=False, help_text='If this is set to true then session is initiated using reverse cobrowsing.'
    )

    agent_session_end_time = models.DateTimeField(
        default=None, null=True, blank=True, help_text="time when agent is closing session")

    client_session_end_time = models.DateTimeField(
        default=None, null=True, blank=True, help_text="time when client closing session")

    agent_notified_count = models.IntegerField(
        default=0, help_text="how many time agent is notified")

    supported_language = models.ForeignKey(
        'LanguageSupport', null=True, blank=True, on_delete=models.CASCADE)

    product_category = models.ForeignKey(
        'ProductCategory', null=True, blank=True, on_delete=models.CASCADE)

    captured_lead = models.ManyToManyField(
        'CobrowseCapturedLeadData', blank=True)

    app_channel = models.TextField(null=True, blank=True)

    feedback_rating = models.TextField(null=True, blank=True)

    is_meeting_only_session = models.BooleanField(
        default=False, help_text="This flag's value will be set only in video meeting only usecase.")

    is_client_in_mobile = models.BooleanField(
        default=False, help_text="This flag will be set only when client's website open in mobile")

    session_archived_cause = models.CharField(
        max_length=100, null=True, blank=True, choices=SESSION_ARCHIVED_CAUSE, help_text="reason of is_archived set to true first time")

    session_archived_datetime = models.DateTimeField(
        default=None, null=True, blank=True, help_text="datetime of is_archived set to true first time")

    browsing_time_before_connect_click = models.IntegerField(
        default=0, help_text="time in seconds spent on website before making cobrowsing request")

    is_droplink_lead = models.BooleanField(
        default=False, help_text="This will be set in case of droplink usecase")

    is_app_cobrowse_session = models.BooleanField(
        default=False, help_text="This will be set if the session is related to app cobrowsing")

    is_lead_converted_by_url = models.BooleanField(
        default=False, help_text="If set True, it would mean that the lead has been converted by landing on one of the URL's mentioned in the console")

    lead_converted_url = models.TextField(
        blank=True, help_text="Stores  on which URL was the lead converted")

    lead_converted_url_datetime = models.DateTimeField(
        default=None, null=True, blank=True, help_text="Datetime of when lead is converted by URL")

    is_lead_manually_converted = models.BooleanField(
        default=False, help_text="If True, it would mean that the lead has been converted manually")

    agent_manually_converted_lead = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                                                      on_delete=models.SET_NULL, related_name='agent_manually_converted_lead', help_text="Agent who converted the lead manually")

    main_primary_agent = models.ForeignKey(CobrowseAgent, null=True, blank=True, related_name="main_primary_agent",
                                           on_delete=models.SET_NULL, help_text="This stores the agent to whom the lead was first assigned to.")

    last_agent_assignment_datetime = models.DateTimeField(
        default=None, null=True, blank=True, help_text="Datetime of when an unattended lead was reassigned to another agent.")

    agents_assigned_list = models.ManyToManyField(
        CobrowseAgent, blank=True, related_name="agents_assigned_list", help_text="A list of agents to whom the unattended lead was reassigned to.")

    is_customer_notified = models.BooleanField(
        default=False, help_text="When an unattended lead is assigned to another agent, this flag is used to check if the customer was notified about the agent change.")

    lead_reassignment_counter = models.IntegerField(
        default=0, help_text="This counter is used to maintain the number of times an unattended lead has been re-assigned.")

    lead_initiated_type_list = (("floating_button", "Floating Button"),
                                ("greeting_bubble", "Greeting Bubble"),
                                ("icon", "Icon"),
                                ("inactivity_popup", "Inactivity Pop-up"),
                                ("exit_intent", "Exit Intent"))

    lead_initiated_by = models.CharField(
        choices=lead_initiated_type_list, max_length=20, null=True, blank=True, help_text='Whether the request was initiated by Floating Button or Greeting Bubble or Exit Intent or Inactivity Pop-up')

    is_cobrowsing_from_livechat = models.BooleanField(
        default=False, help_text="If this toggle is enabled, then it would mean that the current session was initiated from livechat.")

    self_assign_time = models.DateTimeField(
        default=None, null=True, blank=True, help_text='Time at which agent assign lead to himself from queue')

    proxy_key_list = models.ManyToManyField(
        'ProxyCobrowseIO', blank=True, related_name="proxy_key_list", help_text="A list of proxy keys")
        
    cobrowsing_type = models.CharField(
        choices=COBROWSING_TYPE_LIST, max_length=40, null=True, blank=True, help_text='Denotes the type of cobrowsing which is being done')

    def save(self, *args, **kwargs):
        try:
            if self.access_token and self.access_token.enable_masking_pii_data == True and self.is_archived == True:
                self.mobile_number = get_hashed_data(self.mobile_number)

                try:
                    if self.is_lead == True and self.meta_data != None:
                        custom_encrypt_obj = CustomEncrypt()
                        cobrowse_meta_data = custom_encrypt_obj.decrypt(
                            self.meta_data)
                        cobrowse_meta_data = json.loads(cobrowse_meta_data)

                        if "easyassist_sync_data" in cobrowse_meta_data:
                            easyassist_sync_data = cobrowse_meta_data[
                                "easyassist_sync_data"]
                            for easyassist_sync in easyassist_sync_data:
                                easyassist_sync["value"] = get_hashed_data(
                                    easyassist_sync["value"])

                            cobrowse_meta_data[
                                "easyassist_sync_data"] = easyassist_sync_data
                            cobrowse_meta_data = json.dumps(cobrowse_meta_data)
                            self.meta_data = custom_encrypt_obj.encrypt(
                                cobrowse_meta_data)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error On masking easyassist_sync_data  %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error On saving Cobrowseio %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        try:
            super(CobrowseIO, self).save(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving Cobrowseio %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def __str__(self):
        try:
            return str(self.session_id)
        except Exception:
            return "No session"

    def formated_mobile_number(self):
        try:
            number = self.mobile_number
            return format(int(number[:-1]), ",").replace(",", "-") + number[-1]
        except Exception:
            return NO_DETAILS

    def get_meta_data(self):
        try:
            custom_encrypt_obj = CustomEncrypt()
            return custom_encrypt_obj.decrypt(self.meta_data)
        except Exception:
            return self.meta_data

    def product_name(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["title"]
        except Exception:
            return "-"

    def product_description(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["description"]
        except Exception:
            return "-"

    def product_url(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["url"]
        except Exception:
            return "-"

    def get_drop_off_meta_data(self):
        try:
            custom_encrypt_obj = CustomEncrypt()
            return custom_encrypt_obj.decrypt(self.drop_off_meta_data)
        except Exception:
            return self.drop_off_meta_data

    def drop_off_name(self):
        try:
            return json.loads(self.get_drop_off_meta_data())["product_details"]["title"]
        except Exception:
            return "-"

    def drop_off_url(self):
        try:
            return json.loads(self.get_drop_off_meta_data())["product_details"]["url"]
        except Exception:
            return "-"

    def total_time_spent(self):
        try:
            if self.access_token.allow_video_meeting_only:
                try:
                    cobrowse_video_obj = CobrowseVideoConferencing.objects.get(
                        meeting_id=self.session_id)
                    cobrowse_audit_trail_obj = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=cobrowse_video_obj)

                    total_seconds = cobrowse_audit_trail_obj.get_meeting_duration_in_seconds()
                except Exception:
                    total_seconds = 0
            else:
                total_seconds = round(
                    (self.last_agent_update_datetime - self.cobrowsing_start_datetime).total_seconds(), 2)
            if total_seconds < 0:
                return "0 sec"
            hour = total_seconds // 3600
            total_seconds %= 3600
            minutes = total_seconds // 60
            total_seconds %= 60

            time_spent = ""
            if hour > 0:
                time_spent = str(int(hour)) + \
                    (" hours " if hour > 1 else " hour ")
            if minutes > 0:
                time_spent += str(int(minutes)) + \
                    (" mins " if minutes > 1 else " min ")
            time_spent += str(int(total_seconds)) + \
                (" secs" if total_seconds > 1 else " sec")
            return time_spent
        except Exception:
            return "-"

    def total_time_spent_seconds(self):
        time_spent = 0
        try:
            if self.access_token.allow_video_meeting_only:
                try:
                    cobrowse_video_obj = CobrowseVideoConferencing.objects.get(
                        meeting_id=self.session_id)
                    cobrowse_audit_trail_obj = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=cobrowse_video_obj)

                    total_seconds = cobrowse_audit_trail_obj.get_meeting_duration_in_seconds()
                except Exception:
                    total_seconds = 0
            else:
                total_seconds = round(
                    (self.last_agent_update_datetime - self.cobrowsing_start_datetime).total_seconds(), 2)
            if total_seconds < 0:
                total_seconds = 0
            time_spent = total_seconds
        except Exception:
            time_spent = 0

        return round(time_spent)

    def session_time_in_seconds(self):
        try:
            total_seconds = round(
                (self.last_agent_update_datetime - self.cobrowsing_start_datetime).total_seconds(), 2)
            if total_seconds < 0:
                return 0
            return total_seconds
        except Exception:
            return 0

    def customer_wait_time_in_seconds(self):
        try:
            if self.cobrowsing_start_datetime:
                total_seconds = round(
                    (self.cobrowsing_start_datetime - self.request_datetime).total_seconds(), 2)
            elif self.last_update_datetime:
                total_seconds = round(
                    (self.last_update_datetime - self.request_datetime).total_seconds(), 2)
            total_seconds = abs(total_seconds)
            return total_seconds
        except Exception:
            logger.warning("Cobrowsing hasn't been initiated by agent", extra={
                           'AppName': 'EasyAssist'})
            return 0

    def customer_wait_time(self):
        try:
            total_seconds = round(
                (self.cobrowsing_start_datetime - self.request_datetime).total_seconds())
            total_seconds = abs(total_seconds)
            time_spent = ""
            if total_seconds >= 60:
                time_spent = str(round(total_seconds / 60)) + " mins"
            else:
                time_spent = str(total_seconds) + " secs"
            return time_spent
        except Exception:
            logger.warning("Cobrowsing hasn't been initiated by agent", extra={
                'AppName': 'EasyAssist'})
            return "-"

    def customer_wait_time_seconds(self):
        time_spent = 0
        try:
            total_seconds = round(
                (self.cobrowsing_start_datetime - self.request_datetime).total_seconds())
            time_spent = total_seconds
        except Exception:
            logger.warning("Cobrowsing hasn't been initiated by agent", extra={
                'AppName': 'EasyAssist'})
            time_spent = 0
        return time_spent
    
    def lead_in_queue_time(self):
        time_spent_seconds = int((timezone.now() - self.request_datetime).total_seconds())
        time_spent = get_time_in_hours_mins_secs(time_spent_seconds)
        return time_spent

    def get_self_assign_time(self):
        try:
            self_assign_time = self.self_assign_time
            if self_assign_time:
                time_spent_seconds = int((self_assign_time - self.request_datetime).total_seconds())
                self_assign_time = get_time_in_hours_mins_secs(time_spent_seconds)
                return self_assign_time
            else:
                return "-"
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_self_assign_time %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return "-"

    def is_active_timer(self):
        try:
            total_sec = int(
                (timezone.now() - self.last_update_datetime).total_seconds())
            auto_archive_session_timer = self.access_token.auto_archive_cobrowsing_session_timer * 60

            if self.is_archived == False and total_sec > auto_archive_session_timer:
                update_virtual_agent_code(self)
                self.is_archived = True
                self.is_active = False
                description = "Session is archived due to agent inactivity"
                if self.session_archived_cause == None:
                    if self.cobrowsing_start_datetime == None:
                        self.session_archived_cause = "UNATTENDED"
                        self.session_archived_datetime = timezone.now()
                    else:
                        self.session_archived_cause = "CLIENT_INACTIVITY"
                        self.session_archived_datetime = timezone.now()
                        total_min = total_sec // 60
                        description = "Session is archived on inactivity of client for " + \
                            str(total_min) + " minutes"
                self.save()

                category = "session_closed"
                save_system_audit_trail(
                    category, description, self, self.access_token, SystemAuditTrail, sender=None)
                send_page_refresh_request_to_agent(self.agent)

            if self.is_archived:
                return False

            common_inactivity_time_threshold = self.access_token.archive_on_common_inactivity_threshold * 60
            if total_sec > common_inactivity_time_threshold:
                return False
            else:
                return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_active_timer %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def is_agent_active_timer(self):
        try:
            total_sec = (timezone.now() -
                         self.last_agent_update_datetime).total_seconds()
            if total_sec > AGENT_DISCONNECTED_TIME_OUT:
                return False
            else:
                return True
        except Exception:
            return False

    def is_transaction_active_timer(self):
        try:
            total_sec = (timezone.now() -
                         self.init_transaction_datetime).total_seconds()
            if total_sec > 180:
                return False
            else:
                return True
        except Exception:
            return False

    def get_sync_data(self):
        data = NO_DETAILS
        try:
            meta_data = json.loads(self.get_meta_data())
            if "easyassist_sync_data" in meta_data:
                easyassist_sync_data = meta_data["easyassist_sync_data"]
                data = ""
                for easyassist_sync in easyassist_sync_data:
                    sync_value = get_masked_data_if_hashed(
                        easyassist_sync["value"])

                    data += easyassist_sync["name"] + \
                        ": " + sync_value + "<br>"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_sync_data %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return data

    def get_sync_data_formatted(self):
        data = NO_DETAILS
        try:
            easyassist_sync_data = json.loads(self.get_meta_data())[
                "easyassist_sync_data"]
            data = ""
            for easyassist_sync in easyassist_sync_data:
                sync_value = get_masked_data_if_hashed(
                    easyassist_sync["value"])

                data += '<b>' + easyassist_sync["name"] + \
                    ": " + '</b>' + sync_value + "<br>"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_sync_data %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return data

    def get_sync_data_exist(self, search_value):
        try:
            easyassist_sync_data = json.loads(self.get_meta_data())[
                "easyassist_sync_data"]

            for easyassist_sync in easyassist_sync_data:
                if easyassist_sync["value"] == search_value:
                    return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_sync_data_exist %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return False

    def get_sync_data_value(self, search_name):
        try:
            easyassist_sync_data = json.loads(self.get_meta_data())[
                "easyassist_sync_data"]

            for easyassist_sync in easyassist_sync_data:
                if easyassist_sync["name"].lower() == search_name.lower():
                    return get_masked_data_if_hashed(easyassist_sync["value"])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_sync_data_value %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return "-"

    def get_sync_data_name_mobile(self):
        data_value = ["-", "-"]
        try:
            easyassist_sync_data = json.loads(self.get_meta_data())[
                "easyassist_sync_data"]

            for easyassist_sync in easyassist_sync_data:
                if easyassist_sync["name"].lower() == "name":
                    data_value[0] = easyassist_sync["value"]
                if easyassist_sync["name"].lower() == "mobile":
                    data_value[1] = get_masked_data_if_hashed(
                        easyassist_sync["mobile"])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_sync_data_dict %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return data_value

    def get_session_started_by(self):
        if self.is_app_cobrowse_session:
            if self.access_token.enable_app_type == "agent":
                return "Agent"
            else:
                return "Customer"
        
        if self.is_lead or self.is_droplink_lead or self.is_reverse_cobrowsing or self.cobrowsing_type == "outbound-proxy-cobrowsing":
            return "Agent"
        return "Customer"

    def get_cobrowsing_session_meta_data(self):
        return CobrowsingSessionMetaData.objects.filter(cobrowse_io=self)

    def get_cobrowsing_session_closing_comments(self):
        return CobrowseAgentComment.objects.filter(cobrowse_io=self)

    def get_cobrowsing_chat_history(self):
        return CobrowseChatHistory.objects.filter(cobrowse_io=self).order_by('datetime')

    def get_request_access_audit_trail_objs(self):
        request_access_audit_trail_objs = SystemAuditTrail.objects.filter(
            cobrowse_io=self, category="edit_access").order_by('datetime')
        return request_access_audit_trail_objs

    def get_basic_activity_audit_trail_objs(self):
        request_access_audit_trail_objs = SystemAuditTrail.objects.filter(
            cobrowse_io=self, category__in=["session_closed", "session_details", "session_transfer", "session_lead_status_update", "session_transfer_by_supervisor"]).order_by('datetime')
        return request_access_audit_trail_objs

    def get_cobrowse_video_audit_trail_obj(self):
        try:
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=self.session_id)
            if meeting_io.is_voip_meeting:
                audit_trail = CobrowseVideoAuditTrail.objects.get(
                    cobrowse_video=meeting_io)
                return audit_trail
            else:
                return None
        except Exception:
            logger.info("Cobrowsing video meeting does not exist",
                        extra={'AppName': 'EasyAssist'})
            return None

    def get_cobrowse_support_agent_details(self):
        try:
            return CobrowseIOInvitedAgentsDetails.objects.filter(cobrowse_io=self).first()

        except Exception:
            logger.info("Could not get object of CobrowseIOInvitedAgentsDetails for selected CobrowseIO object.",
                        extra={'AppName': 'EasyAssist'})
            return None

    def get_cobrowse_transferred_agent_list(self):
        try:
            transferred_agents = ""
            transferred_agent_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                cobrowse_io=self, cobrowse_request_type="transferred").order_by("log_request_datetime")
            for transferred_agent_obj in transferred_agent_objs:
                transferred_agents = transferred_agents + \
                    str(transferred_agent_obj.transferred_agent.user.email) + " ,"
            if transferred_agents:
                transferred_agents = transferred_agents[:-1]
                return transferred_agents
            return "-"

        except Exception:
            logger.info("Could not get object of CobrowseIOTransferredAgentsLogs for selected CobrowseIO object.",
                        extra={'AppName': 'EasyAssist'})
            return "-"

    def get_cobrowse_transferred_agent_connected_list(self):
        try:
            transferred_agents = ""
            transferred_agent_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                cobrowse_io=self, cobrowse_request_type="transferred", transferred_status="accepted").order_by("log_request_datetime")
            for transferred_agent_obj in transferred_agent_objs:
                transferred_agents = transferred_agents + \
                    str(transferred_agent_obj.transferred_agent.user.email) + " ,"
            if len(transferred_agents):
                transferred_agents = transferred_agents[:-1]
                return transferred_agents
            return "-"

        except Exception:
            logger.info("Could not get object of CobrowseIOTransferredAgentsLogs for selected CobrowseIO object.",
                        extra={'AppName': 'EasyAssist'})
            return "-"

    def get_cobrowse_transferred_agent_rejected_list(self):
        try:
            transferred_agents = ""
            transferred_agent_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                cobrowse_io=self, cobrowse_request_type="transferred", transferred_status__in=["rejected", "expired"]).order_by("log_request_datetime")
            for transferred_agent_obj in transferred_agent_objs:
                transferred_agents = transferred_agents + \
                    str(transferred_agent_obj.transferred_agent.user.email) + " ,"
            if len(transferred_agents):
                transferred_agents = transferred_agents[:-1]
                return transferred_agents
            return "-"

        except Exception:
            logger.info("Could not get object of CobrowseIOTransferredAgentsLogs for selected CobrowseIO object.",
                        extra={'AppName': 'EasyAssist'})
            return "-"

    def get_close_session_message(self):
        if self.access_token.app_close_session_message == None or self.access_token.app_close_session_message == "":
            return "Thank you for being our esteemed customer."
        else:
            message = self.access_token.app_close_session_message
            message = message.replace("{/client_name/}", self.full_name)
            return message

    def check_agent_ended_the_session(self):
        try:
            if self.agent_session_end_time == None:
                return False

            if self.client_session_end_time == None:
                return True

            if self.agent_session_end_time < self.client_session_end_time:
                return True
            else:
                return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error check_agent_ended_the_session %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def is_auto_assign_timer_exhausted(self):
        try:
            if self.access_token.enable_auto_assign_unattended_lead:
                if self.last_agent_assignment_datetime:
                    total_sec = int(
                        (timezone.now() - self.last_agent_assignment_datetime).total_seconds())
                    if total_sec >= self.access_token.auto_assign_unattended_lead_timer:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_auto_assign_timer_exhausted %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def is_transfer_request_timer_exhausted(self):
        try:
            if self.access_token.enable_session_transfer_in_cobrowsing:
                transfer_io_obj = CobrowseIOTransferredAgentsLogs.objects.filter(
                    cobrowse_io=self, cobrowse_request_type="transferred", transferred_status="").order_by("-log_request_datetime").first()
                if transfer_io_obj:
                    total_sec = int(
                        (timezone.now() - transfer_io_obj.log_request_datetime).total_seconds())
                    if total_sec >= self.access_token.transfer_request_archive_time:
                        transfer_io_obj.transferred_status = "expired"
                        transfer_io_obj.save()
                        return True
                    else:
                        return False
            else:
                return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_transfer_timer_exhausted %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def get_transfer_request_remaining_time(self):
        import time
        try:
            remaining_time_details = {
                "remaining_time_str": "-",
                "is_highlight_required": False
            }
            if self.access_token.enable_session_transfer_in_cobrowsing:
                transfer_io_obj = CobrowseIOTransferredAgentsLogs.objects.filter(
                    cobrowse_io=self, cobrowse_request_type="transferred", transferred_status="").order_by("-log_request_datetime").first()
                if transfer_io_obj:
                    transfer_deny_assign_time = transfer_io_obj.log_request_datetime + \
                        datetime.timedelta(
                            seconds=self.access_token.transfer_request_archive_time)
                    time_remaining_before_assignment = int(
                        (transfer_deny_assign_time - timezone.now()).total_seconds())

                    if time_remaining_before_assignment != 0:
                        if time_remaining_before_assignment <= 10:
                            remaining_time_details[
                                "is_highlight_required"] = True
                        time_format = "%M:%S"
                        if time_remaining_before_assignment >= 3600:
                            time_format = "%H:%M:%S"

                        remaining_time_details["remaining_time_str"] = time.strftime(
                            time_format, time.gmtime(time_remaining_before_assignment))
            return remaining_time_details
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_transfer_request_remaining_time %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            remaining_time_details = {
                "remaining_time_str": "-",
                "is_highlight_required": False
            }
            return remaining_time_details

    def is_unattended_lead_timer_elapsed(self):
        try:
            if self.lead_reassignment_counter == self.access_token.unattended_lead_auto_assignment_counter and not \
                    self.is_agent_request_for_cobrowsing and not self.is_cobrowse_session_initiated():

                archive_timer_seconds = self.access_token.auto_assigned_unattended_lead_archive_timer * 60
                total_seconds_elapsed = int(
                    (timezone.now() - self.last_agent_assignment_datetime).total_seconds())

                if total_seconds_elapsed >= archive_timer_seconds:
                    self.is_archived = True
                    self.is_active = False
                    self.session_archived_cause = "UNATTENDED"
                    self.session_archived_datetime = timezone.now()
                    self.save()
                    category = "session_closed"
                    total_min = total_seconds_elapsed // 60
                    description = "Session is archived and stored in unattended leads due to agent not attending it for " + \
                        str(total_min) + " minutes"
                    save_system_audit_trail(
                        category, description, self, self.access_token, SystemAuditTrail, sender=None)
                    send_page_refresh_request_to_agent(self.agent)
                    return True

            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error unattended_lead_timer_elapsed %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def get_readable_auto_assign_remaining_time(self):
        import time
        try:
            remaining_time_details = {
                "remaining_time_str": "-",
                "is_highlight_required": False
            }
            if self.access_token.enable_auto_assign_unattended_lead:
                if self.last_agent_assignment_datetime:

                    # time at which the lead will be auto assigned to next
                    # agent
                    lead_auto_assign_time = self.last_agent_assignment_datetime + \
                        datetime.timedelta(
                            seconds=self.access_token.auto_assign_unattended_lead_timer)
                    time_remaining_before_assignment = int(
                        (lead_auto_assign_time - timezone.now()).total_seconds())

                    if time_remaining_before_assignment != 0:
                        if time_remaining_before_assignment <= 10:
                            remaining_time_details[
                                "is_highlight_required"] = True
                        time_format = "%M:%S"
                        if time_remaining_before_assignment >= 3600:
                            time_format = "%H:%M:%S"

                        remaining_time_details["remaining_time_str"] = time.strftime(
                            time_format, time.gmtime(time_remaining_before_assignment))
            return remaining_time_details
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_readable_auto_assign_remaining_time %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            remaining_time_details = {
                "remaining_time_str": "-",
                "is_highlight_required": False
            }
            return remaining_time_details

    def get_auto_assigned_agents(self):
        try:
            auto_assigned_agents = "-"
            if self.access_token.enable_auto_assign_unattended_lead:
                if self.agents_assigned_list.all():
                    auto_assigned_agents = ""
                    for agent in self.agents_assigned_list.all():
                        auto_assigned_agents += agent.user.username + ", "
                    auto_assigned_agents = auto_assigned_agents[:-2]

            return auto_assigned_agents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_auto_assigned_agents %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def is_cobrowse_session_initiated(self):
        try:
            if self.cobrowsing_start_datetime:
                return True
            elif self.meeting_start_datetime:
                return True
            else:
                return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_cobrowse_session_initiated %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    def get_lead_initiated_by(self):
        try:
            lead_initiated_by = "-"
            lead_initiated = self.lead_initiated_by
            if lead_initiated == 'floating_button':
                lead_initiated_by = "Floating Button"
            elif lead_initiated == 'greeting_bubble':
                lead_initiated_by = "Greeting Bubble"
            elif lead_initiated == 'icon':
                lead_initiated_by = "Icon"
            elif lead_initiated == 'exit_intent':
                lead_initiated_by = "Exit Intent"
            elif lead_initiated == 'inactivity_popup':
                lead_initiated_by = "Inactivity Pop-up"

            return lead_initiated_by
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_lead_initiated_by %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def get_lead_type(self):
        lead_type = ""
        if self.is_lead:
            lead_type = "Outbound"
        elif self.is_reverse_cobrowsing:
            lead_type = "Reverse"
        elif self.is_droplink_lead:
            lead_type = "Drop Link"
        elif self.cobrowsing_type == "modified-inbound" or self.cobrowsing_type == "outbound-proxy-cobrowsing":
            lead_type = self.get_cobrowsing_type_display()
        else:
            lead_type = "Inbound"
        return lead_type
    
    def get_unattended_lead_transfer_audit_trail(self):
        import pytz
        try:
            audit_trail_list = []
            audit_trail_objs = UnattendedLeadTransferAuditTrail.objects.filter(
                cobrowse_io=self).order_by('auto_assign_datetime')
            if audit_trail_objs:
                est = pytz.timezone(settings.TIME_ZONE)
                for audit_trail_obj in audit_trail_objs:
                    agent_details = {
                        "agent_username": audit_trail_obj.auto_assigned_agent.user.username,
                        "auto_assign_datetime": audit_trail_obj.auto_assign_datetime.astimezone(est).strftime("%d-%b-%Y %I:%M %p")
                    }
                    audit_trail_list.append(agent_details)

            return audit_trail_list

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_unattended_lead_transfer_audit_trail %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    class Meta:
        verbose_name = 'CobrowseIO'
        verbose_name_plural = 'CobrowseIO'


class EasyAssistCustomer(models.Model):

    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                   editable=False, help_text='unique user id for each user who is visiting site')

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    full_name = models.CharField(
        default="", max_length=100, null=True, blank=True, help_text='client full name')

    mobile_number = models.CharField(
        default="", max_length=100, null=True, blank=True, help_text='client mobile number')

    title = models.CharField(max_length=1000, null=True, blank=True,
                             help_text='title of webpage from which request has been generated')

    active_url = models.CharField(max_length=1000, null=True, blank=True,
                                  help_text='active webpage url where client is.', db_index=True)

    request_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when lead is generated')

    meta_data = models.TextField(
        null=True, blank=True, help_text='meta data container')

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    request_meta_details = models.TextField(null=True, blank=True)

    lead_initiated_type_list = (("floating_button", "Floating Button"),
                                ("greeting_bubble", "Greeting Bubble"),
                                ("icon", "Icon"),
                                ("exit_intent", "Exit Intent"),
                                ("inactivity_popup", "Inactivity Pop-up"))

    lead_initiated_by = models.CharField(
        choices=lead_initiated_type_list, max_length=20, null=True, blank=True, help_text='Whether the request was initiated by Floating Button or Greeting Bubble or Exit Intent or Inactivity Pop-up')

    def __str__(self):
        try:
            return str(self.customer_id)
        except Exception:
            return "No session"

    def save(self, *args, **kwargs):
        try:
            if self.access_token and self.access_token.enable_masking_pii_data == True:
                self.mobile_number = get_hashed_data(self.mobile_number)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving EasyAssistCustomer %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        try:
            super(EasyAssistCustomer, self).save(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving EasyAssistCustomer %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def get_meta_data(self):
        try:
            custom_encrypt_obj = CustomEncrypt()
            return custom_encrypt_obj.decrypt(self.meta_data)
        except Exception:
            return self.meta_data

    def product_name(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["title"]
        except Exception:
            return "-"

    def product_description(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["description"]
        except Exception:
            return "-"

    def product_url(self):
        try:
            return json.loads(self.get_meta_data())["product_details"]["url"]
        except Exception:
            return "-"

    class Meta:
        verbose_name = 'EasyAssistCustomer'
        verbose_name_plural = 'EasyAssistCustomer'


class CobrowsingSessionMetaData(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, help_text='Cobrowsing session object')

    type_screenshot = models.CharField(
        max_length=100, null=False, blank=False, help_text='Type of screenshot: screenshot|pageshot')

    content = models.TextField(
        null=True, blank=True, help_text='screen image | screen html')

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when meta data is saved')

    def __str__(self):
        return str(self.cobrowse_io.session_id) + " - " + str(self.type_screenshot)

    class Meta:
        verbose_name = 'CobrowsingSessionMetaData'
        verbose_name_plural = 'CobrowsingSessionMetaData'


class CobrowseLeadHTMLField(models.Model):

    tag = models.CharField(
        choices=COBROWSING_HTML_FIELD_TAG, null=False, blank=False, max_length=100)

    tag_name = models.CharField(max_length=100, null=True, blank=True)

    tag_id = models.CharField(max_length=100, null=True, blank=True)

    tag_label = models.CharField(max_length=100, null=False, blank=False)

    tag_reactid = models.CharField(max_length=1000, null=True, blank=True)

    tag_type = models.CharField(
        choices=COBROWSING_HTML_FIELD_TYPE, null=False, blank=False, max_length=100)

    tag_key = models.CharField(max_length=200, null=True, blank=True)

    tag_value = models.CharField(max_length=1000, null=True, blank=True)

    unique_identifier = models.BooleanField(
        default=True, help_text="Marking this field as unique identifier would treat user details generated from this field as a unique detail to display unique or repeated customer count in outbound analytics.")

    is_deleted = models.BooleanField(
        default=False, help_text="If this is set to True, it means that this tag is deleted")

    def __str__(self):
        return str(self.tag) + " - " + str(self.tag_label) + " - " + str(self.tag_type)

    class Meta:
        verbose_name = 'CobrowseLeadHTMLField'
        verbose_name_plural = 'CobrowseLeadHTMLField'


class CobrowseBlacklistedTag(models.Model):

    tag = models.CharField(max_length=100, null=False,
                           blank=False, unique=True)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'CobrowseBlacklistedTag'
        verbose_name_plural = 'CobrowseBlacklistedTag'


class CobrowseObfuscatedField(models.Model):

    key = models.CharField(max_length=200, null=False, blank=False)

    value = models.CharField(max_length=1000, null=False, blank=False)

    masking_type = models.CharField(max_length=30, default="partial-masking", null=False,
                                    blank=False, help_text="Expected values: no-masking, partial-masking, full-masking")

    def __str__(self):
        return str(self.key) + " - " + str(self.value) + " - " + str(self.masking_type)

    class Meta:
        verbose_name = 'CobrowseObfuscatedField'
        verbose_name_plural = 'CobrowseObfuscatedField'


class CobrowseAutoFetchField(models.Model):

    fetch_field_key = models.CharField(max_length=200, null=False, blank=False)

    fetch_field_value = models.CharField(
        max_length=1000, null=False, blank=False)

    modal_field_key = models.CharField(max_length=200, null=False, blank=False)

    modal_field_value = models.CharField(
        max_length=1000, null=False, blank=False)

    def __str__(self):
        return str(self.fetch_field_key) + " - " + str(self.fetch_field_value) + " -- " + str(self.modal_field_key) + " - " + \
            str(self.modal_field_value)

    class Meta:
        verbose_name = 'CobrowseAutoFetchField'
        verbose_name_plural = 'CobrowseAutoFetchField'


class CobrowseDisableField(models.Model):

    key = models.CharField(max_length=200, null=False, blank=False)

    value = models.CharField(max_length=1000, null=False, blank=False)

    def __str__(self):
        try:
            return str(self.key) + " - " + str(self.value)
        except Exception:
            return ""

    class Meta:
        verbose_name = 'CobrowseDisableField'
        verbose_name_plural = 'CobrowseDisableField'


class CobrowseAccessToken(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    agent = models.OneToOneField(CobrowseAgent, on_delete=models.CASCADE,
                                 unique=True, help_text=ADMIN_RESPONSIBLE_FOR_THE_SAME)

    show_floating_easyassist_button = models.BooleanField(
        default=True, help_text="show sidenav for connect with agent action")

    floating_button_left_right_position = models.IntegerField(
        default=0, help_text='Floating button left right position')

    source_easyassist_cobrowse_logo = models.CharField(
        max_length=500, null=True, blank=True, help_text='source of cobrowser logo')

    enable_location = models.BooleanField(
        default=True, help_text='location when customer generated')

    enable_meeting_bgmusic = models.BooleanField(
        default=True, help_text="enable background music in cogno meet")

    show_easyassist_connect_agent_icon = models.BooleanField(
        default=False, help_text="show icon for connect with agent action")

    source_easyassist_connect_agent_icon = models.CharField(
        max_length=100, null=True, blank=True, default="null", help_text='source of connect with agent icon')

    floating_button_position = models.CharField(
        null=True, blank=True, max_length=100, default="left", choices=FLOATING_BUTTON_POSITION)

    floating_button_bg_color = models.CharField(
        null=True, blank=True, max_length=100, default="#0254D7")

    cobrowsing_console_theme_color = models.CharField(
        null=True, blank=True, max_length=200, default=None)

    show_only_if_agent_available = models.BooleanField(
        default=False, help_text="If this true, cobrowsing floating button will be shown only if agents are available.")

    enable_edit_access = models.BooleanField(default=False)

    allow_support_documents = models.BooleanField(
        default=True, help_text="Allow agent to share documents in cobrowsing")

    share_document_from_livechat = models.BooleanField(
        default=True, help_text="Allow sharing documents during livechat in cobrowsing")

    enable_invite_agent = models.BooleanField(
        default=True, help_text="Allow agent to invite other agent in cobrowsing")
        
    field_stuck_event_handler = models.BooleanField(
        default=False, help_text="Enable connect with the agent popup after customer inactivity")

    field_recursive_stuck_event_check = models.BooleanField(
        default=False, help_text="Show connect with the agent popup recursively")

    get_sharable_link = models.BooleanField(default=False)

    lead_generation = models.BooleanField(
        default=True, help_text="Enable search lead functionality")

    enable_inbound = models.BooleanField(
        default=True, help_text="Enable inbound functionality")

    field_stuck_timer = models.IntegerField(default=5)

    proxy_server = models.CharField(max_length=1000, null=True, blank=True)

    connect_message = models.TextField(
        default=CONNECT_MESSAGE)

    assist_message = models.TextField(
        default=ASSIST_MESSAGE)

    meeting_message = models.TextField(
        default="Our Customer Service Agent would like to meet you through video conferencing. By clicking 'Connect' our Customer Service Agent and you will be connected on a video conferencing.")

    voip_with_video_calling_message = models.TextField(
        default=VOIP_WITH_VIDEO_CALLING_MESSAGE)

    voip_calling_message = models.TextField(
        default=VOIP_CALLING_MESSAGE)

    enable_agent_connect_message = models.BooleanField(
        default=False, help_text='If it set as True, A message will be sent to client when Agent first connects')

    agent_connect_message = models.TextField(
        default=AGENT_CONNECT_MESSAGE)

    whitelisted_domain = models.TextField(default="", null=True, blank=True)

    password_prefix = models.TextField(default=DEFAULT_PASSWORD_PREFIX)

    urls_consider_lead_converted = models.TextField(
        default="", null=True, blank=True)

    restricted_urls = models.TextField(
        default="", null=True, blank=True)

    strip_js = models.BooleanField(default=True)

    is_socket = models.BooleanField(default=True)

    search_fields = models.ManyToManyField('CobrowseLeadHTMLField', blank=True)

    blacklisted_tags = models.ManyToManyField(
        'CobrowseBlacklistedTag', blank=True)

    obfuscated_fields = models.ManyToManyField(
        'CobrowseObfuscatedField', blank=True)

    auto_fetch_fields = models.ManyToManyField(
        'CobrowseAutoFetchField', blank=True)

    disable_fields = models.ManyToManyField(
        'CobrowseDisableField', blank=True)

    is_active = models.BooleanField(default=True)

    custom_select_remove_fields = models.ManyToManyField(
        'CobrowseCustomSelectRemoveField', blank=True)

    enable_greeting_bubble = models.BooleanField(
        default=True, help_text="Enable Greeting Bubble functionality")

    greeting_bubble_auto_popup_timer = models.IntegerField(default=5)

    greeting_bubble_text = models.TextField(
        default="Welcome, Please click here to request for agent assistance.")

    # To save the inactivity count
    inactivity_auto_popup_number = models.IntegerField(default=5)

    # display agent profile
    display_agent_profile = models.BooleanField(
        default=True, help_text="toggle to display the agent profile picture")

    # deprecated field
    partial_masking = models.BooleanField(
        default=True, help_text='If it is set to True then data will be masked partially else it will be full masked')

    allow_only_support_documents = models.BooleanField(
        default=False, help_text='If it is set to True then file upload button in chat window would be not shown')

    masking_type = models.CharField(
        max_length=30, default="partial-masking", null=True, blank=True, help_text="Expected values: no-masking, partial-masking, full-masking")

    enable_verification_code_popup = models.BooleanField(
        default=True, help_text='If it is set to True then verification code is asked to customers')

    show_verification_code_modal = models.BooleanField(
        default=True, help_text='If it is set to True then verification code modal will be shown to customers')

    disable_connect_button_if_agent_unavailable = models.BooleanField(
        default=False, help_text='If it is set to True then connect with agent button is disabled')

    message_if_agent_unavailable = models.TextField(
        default=AGENT_UNAVAILABLE_MESSAGE, null=True, blank=True, help_text='Message shown to customer on hovering on connect button when agents are unavailable')

    enable_non_working_hours_modal_popup = models.BooleanField(
        default=False, help_text='If it is set to True then non working hours modal will be displayed')

    message_on_non_working_hours = models.TextField(
        default=NON_WORKING_HOURS_MESSAGE, null=True, blank=True, help_text='Message shown to customer on non-working hours')

    show_connect_confirmation_modal = models.BooleanField(
        default=True, help_text='If it is set to True then connect confirmation modal is shown to customers')

    message_on_connect_confirmation_modal = models.TextField(
        default="Thank you, we have captured your details. We will notify you as soon as our agent connects with you.",
        null=True, blank=True, help_text='Message shown on connect confirmation modal')

    client_id = models.CharField(
        max_length=100, null=True, blank=True, help_text='Client id for authentication')

    client_key = models.CharField(
        max_length=100, null=True, blank=True, help_text='Client key for authentication')

    start_time = models.TimeField(default=datetime.time(
        0, 0, 0), null=True, blank=True, help_text="start time to show button")

    end_time = models.TimeField(default=datetime.time(
        23, 59, 0), null=True, blank=True, help_text="end time till show button")

    cobrowse_agent_working_days = models.TextField(
        default=json.dumps(COBOWSE_AGENT_WORKING_DAYS), blank=True, null=True, help_text="working days of cobrowse agent")

    allow_generate_meeting = models.BooleanField(
        default=True, help_text='If it is set to True then agent will able to generate meeting.')

    enable_cognomeet = models.BooleanField(
        default=False, help_text='Enable third party for video calling (Dyte)')

    enable_screen_sharing = models.BooleanField(
        default=True, help_text='If enabled participants will be able to share screen in cogno meet')

    enable_voip_calling = models.BooleanField(default=False)

    customer_initiate_voice_call = models.BooleanField(default=False)

    enable_auto_voip_calling_for_first_time = models.BooleanField(
        default=True, help_text="If it is set to True, then audio call will be initiated for the first time when agent join the cobrowsing session")

    enable_voip_with_video_calling = models.BooleanField(default=True)

    customer_initiate_video_call_as_pip = models.BooleanField(default=False)

    enable_auto_voip_with_video_calling_for_first_time = models.BooleanField(
        default=True, help_text="If it is set to True, then video call will be initiated for the first time when agent join the cobrowsing session")

    allow_video_meeting_only = models.BooleanField(default=False)

    enable_optimized_cobrowsing = models.BooleanField(
        default=True, help_text='If it is set then new optimized cobrowsing will be used')

    cobrowsing_sync_html_interval = models.IntegerField(default=1000)

    enable_custom_cobrowse_dropdown = models.BooleanField(
        default=True, help_text='If it is set then  browser dropdown of the website will be replaced by custom cobrowsing dropdown')

    meeting_default_password = models.CharField(
        max_length=2048, default="", null=True, blank=True)

    meeting_host_url = models.CharField(
        max_length=2048, default='meet-uat.allincall.in')

    allow_meeting_feedback = models.BooleanField(default=True)

    allow_cobrowsing_meeting = models.BooleanField(
        default=False, help_text='If it is set to True then agent will able to do meeting in cobrowsing.')

    customer_initiate_video_call = models.BooleanField(default=False)

    show_cobrowsing_meeting_lobby = models.BooleanField(
        default=True, help_text='If it is set to True then agent and client will able to see lobby page of meeting in cobrowsing.')

    allow_meeting_end_time = models.BooleanField(
        default=False, help_text='If it is set to True then admin can set the meeting end time.')

    meeting_end_time = models.CharField(max_length=10, default="60", null=True, blank=True,
                                        help_text='Meeting will ended after this much time and all the members will be out.')

    go_live_date = models.DateField(
        null=True, blank=True, default=datetime.date.today, help_text='date when the project has gone live')

    allow_language_support = models.BooleanField(
        default=False, help_text='Designates weather language support enable or not.')

    allow_screen_recording = models.BooleanField(
        default=False, help_text='Designates weather screen recording in cobrowsing is enabled or not.')

    recording_expires_in_days = models.IntegerField(
        default=30, help_text='After this many days, the recording will be deleted.')

    lead_conversion_checkbox_text = models.CharField(
        max_length=2048, default='Lead has been closed successfully.', help_text='text to be shown in lead conversion checkbox in agent feedback form')

    search_lead_label_text = models.CharField(
        max_length=2048, default='', null=True, blank=True, help_text='Text to be shown in search lead label')

    ask_client_mobile = models.BooleanField(
        default=True, help_text='If it is set as True, mobile number will be asked while connecting with agent')

    is_client_mobile_mandatory = models.BooleanField(
        default=True, help_text='If ask_client_mobile is True, and this is set as True then mobile number will be mandatory, else optional')

    allow_popup_on_browser_leave = models.BooleanField(
        default=False, help_text='If this is True, then on browser leave event popup will come up')

    no_of_times_exit_intent_popup = models.IntegerField(
        default=1, help_text='It is the maximum no of times a exit intent modal will popup')

    enable_recursive_browser_leave_popup = models.BooleanField(
        default=False, help_text='If this is True then on browser leave event popup will come up every time')

    allow_connect_with_virtual_agent_code = models.BooleanField(
        default=False, help_text='Allow connect with an agent with virtual agent code')

    connect_with_virtual_agent_code_mandatory = models.BooleanField(
        default=False, help_text='If true, then it would be compulsory for the customer to enter the agent code.')

    allow_screen_sharing_cobrowse = models.BooleanField(
        default=False, help_text='If it is set as True, screensharing will enabled during cobrowsing.')

    allow_connect_with_drop_link = models.BooleanField(
        default=True, help_text='Allow connect with an agent using drop link')

    choose_product_category = models.BooleanField(
        default=False, help_text='If it is set as True, customer will be asked to choose product category')

    enable_predefined_remarks = models.BooleanField(
        default=False, help_text='If it set as True, Agent will choose a remark from dropdown')

    enable_predefined_subremarks = models.BooleanField(
        default=False, help_text='If it set as True, Agent will choose a subremark from dropdown')

    enable_predefined_remarks_with_buttons = models.BooleanField(
        default=False, help_text='If it set as True, Agent will choose a remark from buttons shown')

    predefined_remarks = models.TextField(
        null=True, blank=True, default="[]", help_text='Remarks added by the admin will be added here seprated by comma and shown as dropdown')

    predefined_remarks_with_buttons = models.TextField(
        null=True, blank=True, default="", help_text='Remarks added by the admin will be added here seprated by comma and shown as buttons')

    predefined_remarks_optional = models.BooleanField(
        default=True, help_text='If it is set as True, adding remarks and subremarks will not be mandatory')

    message_on_choose_product_category_modal = models.TextField(
        default=MESSAGE_ON_CHOOSE_PRODUCT_CATEGORY_MODAL,
        null=True, blank=True, help_text='Message shown on choose product category modal')

    highlight_api_call_frequency = models.IntegerField(
        default=10, help_text="Default Customer side status check API call frequency in secs")

    allow_file_verification = models.BooleanField(
        default=False, help_text="If this is true, client's uploaded file on the website will be sent to the agent's chatbox")

    allow_agent_to_customer_cobrowsing = models.BooleanField(
        default=False, help_text='Allow agent to reverse cobrowsing')

    allow_agent_to_screen_record_customer_cobrowsing = models.BooleanField(
        default=False, help_text='Allow agent to screen record in reverse cobrowsing')

    allow_agent_to_audio_record_customer_cobrowsing = models.BooleanField(
        default=False, help_text='Allow agent to audio record in reverse cobrowsing')

    enable_waitlist = models.BooleanField(
        default=False, help_text='Allow admin to enable waitlist')

    show_floating_button_on_enable_waitlist = models.BooleanField(
        default=False, help_text='If its value is True and enable_waitlist is True, floating button will be shown')

    archive_on_unassigned_time_threshold = models.IntegerField(
        default=10, help_text='All the Cobrowsing requests older than the given time threshold will be archived Automatically [in minutes]')

    archive_message_on_unassigned_time_threshold = models.TextField(
        default=UNASSIGNED_LEAD_DEFAULT_MESSAGE, help_text='This is the message that will be shown to the customer when the lead gets archived after the archive_on_unassigned_time_threshold timer drains down.')

    archive_on_common_inactivity = models.BooleanField(
        default=True, help_text='Flag : If inactivity of agent/client more then this threshold is detected then lead will be archived')

    archive_on_common_inactivity_threshold = models.IntegerField(
        default=20, help_text='If inactivity of agent/client more then this threshold is detected then lead will be archived [in minutes]')

    maximum_active_leads = models.BooleanField(
        default=True, help_text='If this is enabled then maximum maximum_active_leads_threshold active leads will be assigned to agent')

    maximum_active_leads_threshold = models.IntegerField(
        default=3, help_text="Maximum number of Cobrowsing and Inbound Meeting Requests that can be assigned to an agent")
    
    enable_request_in_queue = models.BooleanField(
        default=True, help_text="Enabling this will allow agents to pick any lead from he dashboard")

    supervisor_agent_creation_limit = models.IntegerField(
        default=2, null=True, blank=True, help_text="No of the agents can be created by supervisors.")

    adminally_agent_creation_limit = models.IntegerField(
        default=2, null=True, blank=True, help_text="No of the agents can be created by admin allies.")

    adminally_supervisor_creation_limit = models.IntegerField(
        default=2, null=True, blank=True, help_text="No of the supervisors can be created by admin allies.")

    is_droplink_email_mandatory = models.BooleanField(
        default=False, help_text="Enabling this will make the mail field in GDL DropLink modal mandatory")

    # App Cobrowsing

    bitmap_compress_ratio = models.IntegerField(default=25)

    app_client_logo = models.FileField(
        upload_to="app_logos/", null=True, blank=True)

    app_cobrowse_logo = models.FileField(
        upload_to="app_logos/", null=True, blank=True)

    app_close_session_message = models.TextField(null=True, blank=True)

    app_allow_public_document_sharing = models.BooleanField(default=False)

    app_client_document_sharing_allowed = models.BooleanField(default=True)

    app_capping_max_connections = models.BooleanField(
        default=False, help_text="Cap maximum connection allow to cobrowse")

    enable_app_type = models.CharField(choices=(("customer", "customer"), ("agent", "agent")),
                                       max_length=20, null=True, blank=True, help_text='type of app', default="agent")

    enable_app_type_search_lead = models.BooleanField(default=False)

    enable_app_cobrowsing = models.BooleanField(default=True)

    enable_app_link_sharing = models.BooleanField(default=True)

    enable_app_chat_dialog = models.BooleanField(default=True)

    enable_app_video_kyc_dialog = models.BooleanField(default=True)

    enable_app_photo_kyc_dialog = models.BooleanField(default=True)

    enable_app_audio_call_dialog = models.BooleanField(default=True)

    enable_app_video_conferencing_dialog = models.BooleanField(default=True)

    enable_app_screen_share_dialog = models.BooleanField(default=True)

    enable_app_youtube_player = models.BooleanField(
        default=True, help_text="If enabled, one would be able to play youtube videos in the Jitsi Call")

    enable_request_edit_access_dialog = models.BooleanField(default=True)

    enable_inapp_cobrowsing = models.BooleanField(default=True)

    enable_app_field_masking = models.BooleanField(default=False)

    enable_app_quick_access_tray = models.BooleanField(default=False)

    enable_app_screen_border = models.BooleanField(default=False)

    enable_app_system_file_picker = models.BooleanField(
        default=False, help_text="If enabled, the user would be able to upload files into the chat which are present in his device")

    enable_capture_client_screenshot = models.BooleanField(
        default=False, help_text="If enabled, the agent would be able to capture the screenshot of the client's mobile screen which is visible to him on the browser")

    app_inactivity_timer = models.IntegerField(
        default=25, help_text="Session Inactivity timer in minutes")

    app_close_session_timer = models.IntegerField(
        default=5, help_text="Session inactivity timer in minutes")

    app_client_share_link_message = models.TextField(
        default=DEFAULT_APP_COBROWSING_CUSTOMER_SHARE_MESSAGE, null=True, blank=True)

    app_expert_share_link_message = models.TextField(
        default=DEFAULT_APP_COBROWSING_EXPERT_SHARE_MESSAGE, null=True, blank=True)

    meet_background_color = models.CharField(
        null=True, blank=True, max_length=100, default="#474747")

    enable_masked_field_warning = models.BooleanField(default=False)

    masked_field_warning_text = models.TextField(
        default=MASKED_FIELD_WARNING_TEXT, help_text="Maksed Field Warning to be shown to Customer")

    enable_video_conferencing_form = models.BooleanField(default=False)

    enable_followup_leads_tab = models.BooleanField(default=True)

    advanced_setting_static_file_action = models.CharField(
        max_length=100, null=True, blank=True, default="nochange", choices=STATIC_FILE_ACTION_CHOICES, help_text="Please do not use it, this is only for development.")

    no_agent_connects_toast = models.BooleanField(
        default=True, help_text="If Agent is unable to connect with the customer then show message to customer")

    no_agent_connects_toast_text = models.TextField(default=NO_AGENT_CONNECTS_TOAST_TEXT, null=True, blank=True,
                                                    help_text='If Agent is unable to connect with the customer then show this message to customer')

    no_agent_connects_toast_threshold = models.IntegerField(
        default=1, help_text='If Agent is unable to connect with the customer then message will be shown to customer after this time [in minutes]')

    no_agent_connects_toast_reset_count = models.IntegerField(
        default=2, help_text='Denotes the number of times the timer would run post it\'s first execution. If the value is 0, the timer would only run once. If 1, timer would run twice.')

    no_agent_connects_toast_reset_message = models.TextField(default=NO_AGENT_CONNECTS_TOAST_RESET_MESSAGE, null=True, blank=True,
                                                             help_text='This message will be shown to the customer once the timer reset count is exhausted')

    enable_no_agent_connects_toast_meeting = models.BooleanField(
        default=True, help_text="If enabled and if Agent is unable to connect with the customer during a meeting then show message to customer")

    no_agent_connects_meeting_toast_text = models.TextField(default=NO_AGENT_CONNECTS_TOAST_TEXT_MEETING, null=True, blank=True,
                                                            help_text='If Agent is unable to connect with the customer during a meeting then show this message to customer')

    no_agent_connects_meeting_toast_threshold = models.IntegerField(
        default=1, help_text='If Agent is unable to connect with the customer during a meeting then no_agent_connects_meeting_toast_text will be shown to customer after this time [in minutes]')

    show_floating_button_after_lead_search = models.BooleanField(
        default=True, help_text="If this flag is true then support button will be visible after search lead.")

    enable_screenshot_agent = models.BooleanField(
        default=True, help_text="Allow agent to capture screenshots in cobrowsing")

    enable_invite_agent_in_cobrowsing = models.BooleanField(
        default=True, help_text="Allow agent to invite other agent in cobrowsing")

    enable_session_transfer_in_cobrowsing = models.BooleanField(
        default=True, help_text="Allow agent to transfer cobrowse session to other agent during cobrowsing")

    transfer_request_archive_time = models.IntegerField(
        default=120, help_text='Mark transferred lead as expired after the time [in seconds]')

    allow_capture_screenshots = models.BooleanField(
        default=True, help_text="Allow agent to caputer screenshots in cogno meet")

    enable_invite_agent_in_meeting = models.BooleanField(
        default=True, help_text="Allow agent to invite other agent in meetings")

    enable_tag_based_assignment_for_outbound = models.BooleanField(
        default=False, help_text="If this flag is true then agent can search only those product category which they support.")

    disable_auto_offline_agent = models.BooleanField(
        default=False, help_text="If this flag is true then agent will not be automatically offline after 30 sec of inactivity")

    auto_archive_cobrowsing_session_timer = models.IntegerField(
        default=60, help_text="Cobrowsing session auto archive time in minutes")

    drop_link_expiry_time = models.IntegerField(
        default=DEFAULT_DROP_LINK_EXPIRY_TIME, help_text="Drop link expiry time in minutes")

    enable_masking_pii_data = models.BooleanField(
        default=True, help_text="Designates whether masking pii data is enabled or not")

    enable_low_bandwidth_cobrowsing = models.BooleanField(
        default=True, help_text="Flag to enable low bandwidth cobrowsing.")

    enable_manual_switching = models.BooleanField(
        default=True, help_text="Flag to enable manual switching between lite mode and normal mode cobrowsing.")

    low_bandwidth_cobrowsing_threshold = models.IntegerField(
        default=1024, help_text="Network threshold below which low bandwidth cobrowsing work")

    bug_report_mails = models.TextField(
        null=True, blank=True, default="csm@getcogno.ai", help_text='Email ids on which bugs will be reported, seprated by comma')

    enable_cobrowsing_annotation = models.BooleanField(
        default=True, help_text="Enable Agent to draw on cobrowsing page")

    enable_cobrowsing_on_react_website = models.BooleanField(
        default=False, help_text="Enable cobrowsing on react websites")

    deploy_chatbot_flag = models.BooleanField(
        default=False, help_text="Enabling this will allow you to integrate a chatbot to the cobrowsing console")

    deploy_chatbot_url = models.TextField(
        default="", null=True, blank=True, help_text='CJS script of your chatbot')

    font_family = models.TextField(
        default="Silka", null=True, blank=True, help_text='EasyAssist font')

    enable_mailer_analytics = models.BooleanField(
        default=False, help_text="Enable mailer analytics")

    show_agent_details_modal = models.BooleanField(
        default=True, help_text="If true, agent details modal will be visible at customer end when agent joins the session")

    show_agent_email = models.BooleanField(
        default=True, help_text="If true, agent Email ID will be visible in Agent Details pop up at customer end")

    enable_meeting_recording = models.BooleanField(
        default=True, help_text="Enable recording in meeting")

    enable_iframe_cobrowsing = models.BooleanField(
        default=True, help_text="If true, cobrowsing can also be done in iframe")

    enable_chat_functionality = models.BooleanField(
        default=True, help_text="Enable chat in cobrowsing and meeting")

    enable_preview_functionality = models.BooleanField(
        default=True, help_text="Enable document preview in cobrowsing")

    enable_smart_agent_assignment = models.BooleanField(
        default=False, help_text="Enable smart agent assignment in cobrowsing")

    smart_agent_assignment_reconnecting_window = models.IntegerField(
        default=10)

    enable_auto_assign_unattended_lead = models.BooleanField(
        default=False, help_text="If true, the leads which are not attended after a specific amount of time (auto_assign_unattended_lead_timer) will be assigned to another agent")

    assign_agent_under_same_supervisor = models.BooleanField(
        default=False, help_text="If this toggle is enabled, an unattended lead would be re-assigned to an agent who is mapped under the present assigned agent's supervisor.")

    auto_assign_unattended_lead_timer = models.IntegerField(
        default=100, help_text="Time (in secs) after which an unattended lead would be assigned to the next available agent.")

    auto_assign_unattended_lead_message = models.TextField(default=AUTO_ASSIGN_UNATTENDED_LEAD_MESSAGE, null=True, blank=True,
                                                           help_text="Message to be displayed to customer when the lead is being assigned to another agent.")

    enable_auto_assign_to_one_agent = models.BooleanField(
        default=True, help_text="If this toggle is enabled, an unattended lead would be re-assigned to only one agent and if that agent does not attend the lead then it will be registered as unattended when auto archive time is elapsed")

    auto_assigned_unattended_lead_archive_timer = models.IntegerField(
        default=10, help_text="Time (in mins) after which an unattended lead would be marked as archived post last assignment to an agent (Works only when enable_auto_assign_to_one_agent is enabled).")

    unattended_lead_auto_assignment_counter = models.IntegerField(
        default=2, help_text="Specifies the number of times the lead would be auto assigned to another available agent.")

    auto_assign_lead_end_session_message = models.TextField(default=AUTO_ASSIGN_LEAD_END_SESSION_MESSAGE, null=True, blank=True,
                                                            help_text="Message to be displayed to customer when the lead has been archived post reassignment to agents.")

    jaas_authentication = models.TextField(default="{}")

    jaas_private_key = models.TextField(default="")

    enable_chat_bubble = models.BooleanField(
        default=True, help_text="Enables the chat bubble during live chat")

    enable_lead_status = models.BooleanField(
        default=True, help_text="Enabling this toggle would add a new tab to display lead status inside Active Customers")

    chat_bubble_icon_source = models.CharField(
        max_length=100, null=True, blank=True, default="", help_text='source of chat bubble icon')
    
    cogno_meet_access_token = models.CharField(
        max_length=200, null=True, blank=True, default="", help_text='Access token key for CognoMeetApp')

    def save(self, *args, **kwargs):

        if self.agent.user.username != None and self.agent.user.username.endswith("@getcogno.ai"):
            self.whitelisted_domain = "*"

        if self.advanced_setting_static_file_action == "reset":
            create_static_files_access_token_specific(self, reset=True)
            self.advanced_setting_static_file_action = "nochange"
        elif self.advanced_setting_static_file_action == "update":
            create_static_files_access_token_specific(self, reset=False)
            self.advanced_setting_static_file_action = "nochange"

        super(CobrowseAccessToken, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.key) + " - " + str(self.agent.user.username)

    def is_valid_domain(self, domain):
        try:
            if self.whitelisted_domain == None:
                return False

            if self.whitelisted_domain == "":
                return False

            if self.whitelisted_domain == "*":
                return True

            whitelisted_domain = self.whitelisted_domain.split(",")
            whitelisted_domain = [w_domain.strip().lower()
                                  for w_domain in whitelisted_domain if w_domain != ""]

            if domain.strip().lower() in whitelisted_domain:
                return True
            else:
                return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_valid_domain %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return False

    def get_static_file_token_wise_list_specific_type(self, file_type):
        try:
            saved_file_name_list = STATIC_FILE_TOKEN_WISE_LIST
            file_info_obj_list = []

            for file_info_obj in saved_file_name_list:
                if file_info_obj.split("/")[0] == file_type:
                    file_name = file_info_obj.split("/")[1]
                    relative_path = "EasyAssistApp/static/EasyAssistApp/" + \
                        file_type + "/" + str(self.key) + "/" + file_name
                    file_info_obj_list.append(
                        {"type": file_type, "name": file_name, "relative_path": relative_path})

            return file_info_obj_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_static_file_token_wise_list_specific_type %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    def get_static_file_token_wise_list(self):
        try:
            file_info_obj_list = []
            file_info_obj_list += self.get_static_file_token_wise_list_specific_type(
                "js")
            file_info_obj_list += self.get_static_file_token_wise_list_specific_type(
                "css")
            file_info_obj_list += self.get_static_file_token_wise_list_specific_type(
                "img")
            return file_info_obj_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_static_file_token_wise_list %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    def get_start_time(self):
        try:
            start_time = str(self.start_time)
            return start_time[0:5]
        except Exception:
            return "00:00"

    def get_end_time(self):
        try:
            end_time = str(self.end_time)
            return end_time[0:5]
        except Exception:
            return "23:59"

    def get_url_list_where_consider_lead_converted(self):
        try:
            urls = self.urls_consider_lead_converted
            url_list = urls.split(",")
            return url_list
        except Exception:
            return []

    def get_restricted_urls_list(self):
        try:
            urls = self.restricted_urls
            url_list = urls.split(",")
            return url_list
        except Exception:
            return []

    def get_supported_languages(self):
        supported_language = ""
        try:
            for item in self.agent.supported_language.filter(is_deleted=False).order_by('index'):
                supported_language += str(item.title).strip() + ", "

            if len(supported_language) > 2:
                return supported_language[:-2]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_supported_languages %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_product_categories(self):
        product_category = ""
        try:
            for item in self.agent.product_category.filter(is_deleted=False).order_by('index'):
                product_category += str(item.title) + ", "

            if len(product_category) > 2:
                return product_category[:-2]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_product_categories %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_client_logo(self):
        try:
            return settings.EASYCHAT_HOST_URL + self.app_client_logo.url
        except Exception:
            return ""

    def get_color_by_percent(self, color_obj, percent):
        try:
            red = color_obj["red"]
            green = color_obj["green"]
            blue = color_obj["blue"]

            red = int(red * (100 + percent) / 100)
            green = int(green * (100 + percent) / 100)
            blue = int(blue * (100 + percent) / 100)

            red = min(red, 255)
            green = min(green, 255)
            blue = min(blue, 255)

            red = hex(red).lstrip('0x').rstrip('L')
            green = hex(green).lstrip('0x').rstrip('L')
            blue = hex(blue).lstrip('0x').rstrip('L')

            if len(red) == 0:
                red = "0"
            if len(green) == 0:
                green = "0"
            if len(blue) == 0:
                blue = "0"

            if len(red) == 1:
                red = "0" + red
            if len(green) == 1:
                green = "0" + green
            if len(blue) == 1:
                blue = "0" + blue

            new_color_hex = "#" + red + green + blue
            return new_color_hex
        except Exception:
            return None

    def get_dark_theme_color(self):
        try:
            cobrowsing_console_theme_color = json.loads(
                self.cobrowsing_console_theme_color)
            return self.get_color_by_percent(cobrowsing_console_theme_color, -26)
        except Exception:
            return None

    def get_cobrowsing_console_theme_color(self):
        try:
            cobrowsing_console_theme_color = json.loads(
                self.cobrowsing_console_theme_color)
            return cobrowsing_console_theme_color
        except Exception:
            return None

    def get_assign_task_processor_obj(self):
        try:
            assign_task_processor = AssignTaskProcessor.objects.filter(
                access_token=self).first()
            if assign_task_processor == None:
                assign_task_processor = AssignTaskProcessor.objects.create(
                    access_token=self)
            return assign_task_processor
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_assign_task_processor_obj %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def get_cobrowsing_theme_color_rgb(self):
        try:
            cobrowsing_theme_color = self.floating_button_bg_color
            red = cobrowsing_theme_color[1:3]
            green = cobrowsing_theme_color[3:5]
            blue = cobrowsing_theme_color[5:]

            red = int(red, 16)
            green = int(green, 16)
            blue = int(blue, 16)

            return {
                "red": red,
                "green": green,
                "blue": blue,
            }
        except Exception:
            return {
                "red": 255,
                "green": 0,
                "blue": 0,
            }

    def get_cobrowse_working_days(self):
        try:
            working_days = json.loads(self.cobrowse_agent_working_days)
            return working_days
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_cobrowse_working_days %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    def get_api_integration_manager_obj(self):
        try:
            api_integration_obj = EasyAssistAPIIntegrationManager.objects.filter(
                access_token=self).first()
            if api_integration_obj:
                return api_integration_obj
            else:
                api_integration_obj = EasyAssistAPIIntegrationManager.objects.create(
                    access_token=self)
                return api_integration_obj

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_api_integration_obj %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def is_agent_details_api_enabled(self):
        try:
            api_integration_obj = self.get_api_integration_manager_obj()
            return api_integration_obj.enable_agent_details_api

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_api_integration_obj %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def get_agent_details_api_processor_obj(self):
        try:
            agent_details_api_processor_obj = AgentDetailsAPIProcessor.objects.filter(
                access_token=self).first()
            if agent_details_api_processor_obj:
                return agent_details_api_processor_obj
            else:
                agent_details_api_processor_obj = AgentDetailsAPIProcessor.objects.create(
                    access_token=self)
            return agent_details_api_processor_obj
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_agent_details_api_processor_obj %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def get_proxy_config_obj(self):
        try:
            proxy_config_obj = ProxyCobrowseConfig.objects.filter(
                access_token=self).first()

            if not proxy_config_obj:
                proxy_config_obj = ProxyCobrowseConfig.objects.create(
                    access_token=self)

            return proxy_config_obj
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in get_proxy_config_obj %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None

    class Meta:
        verbose_name = 'CobrowseAccessToken'
        verbose_name_plural = 'CobrowseAccessToken'


@receiver(post_save, sender=CobrowseAccessToken)
def post_token_save(sender, instance, created, *args, **kwargs):
    if not kwargs["raw"] and created:
        create_static_files_access_token_specific(instance, reset=True)


class AppCobrowseMaskedFields(models.Model):

    cobrowse_access_token = models.ForeignKey(
        CobrowseAccessToken, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    activity_name = models.CharField(max_length=200, null=False, blank=False,
                                     help_text="Name of the android activity in which masking has to be done")

    ids = models.CharField(max_length=1000, null=False, blank=False,
                           help_text="Name of the ID's of the fields on which masking has to be done (Enter comma seperated values)")

    def __str__(self):
        try:
            return str(self.activity_name) + " - " + str(self.ids)
        except Exception:
            return ""

    class Meta:
        verbose_name = 'AppCobrowseMaskedFields'
        verbose_name_plural = 'AppCobrowseMaskedFields'


class CobrowsePIIDataOTP(models.Model):
    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text='agent who is responsible action')

    otp = models.CharField(max_length=200)

    def __str__(self):
        return str(self.user.user.username)

    class Meta:
        verbose_name = 'CobrowsePIIDataOTP'
        verbose_name_plural = 'CobrowsePIIDataOTP'


class CobrowsingMiddlewareAccessToken(models.Model):

    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    timestamp = models.DateTimeField(default=timezone.now)

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'CobrowsingMiddlewareAccessToken'
        verbose_name_plural = 'CobrowsingMiddlewareAccessToken'


class SecuredLogin(models.Model):

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True, related_name='SecuredLoginUser')

    failed_attempts = models.IntegerField(default=0)

    last_attempt_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True)

    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def last_attempted_datetime_secs(self):
        return (timezone.now() - self.last_attempt_datetime).total_seconds()

    class Meta:
        verbose_name = 'SecuredLogin'
        verbose_name_plural = 'SecuredLogin'


class CobrowsingAuditTrail(models.Model):

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text='agent who is responsible action')

    action = models.CharField(
        max_length=100, null=True, blank=True, choices=COBROWSING_ACTION_LIST)

    datetime = models.DateTimeField(default=timezone.now)

    action_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.agent.user.username + " - " + self.action

    def get_action(self):
        if self.action == None:
            return "No-action"

        return COBROWSING_ACTION_DICT[self.action]

    class Meta:
        verbose_name = "CobrowsingAuditTrail"


class CobrowseDropLink(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique drop link key')

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text='agent who generated drop link')

    client_page_link = models.CharField(
        max_length=1000, null=True, blank=True)

    customer_name = models.CharField(
        max_length=1000, null=True, blank=True)

    customer_mobile = models.CharField(
        max_length=1000, null=True, blank=True)

    customer_email = models.CharField(
        max_length=1000, null=True, blank=True)

    generated_link = models.CharField(
        max_length=1000, null=True, blank=True)

    generate_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when link was generated')

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    is_pii_data_masked = models.BooleanField(default=False)

    proxy_cobrowse_io = models.ForeignKey(
        'ProxyCobrowseIO', on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Proxy cobrowse session id')
    
    def mask_customer_details(self):

        try:
            if self.cobrowse_io and self.cobrowse_io.access_token.enable_masking_pii_data == True and self.cobrowse_io.is_archived:
                self.customer_mobile = get_hashed_data(self.customer_mobile)
                self.customer_email = get_hashed_data(self.customer_email)
                self.is_pii_data_masked = True
                self.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CobrowseDropLink %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def is_link_valid(self):
        try:
            total_sec = int(
                (timezone.now() - self.generate_datetime).total_seconds())
            drop_link_expiry_time = self.agent.get_access_token_obj().drop_link_expiry_time * 60
            if total_sec > drop_link_expiry_time:
                return False
            else:
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on checking if drop link is valid CobrowseDropLink %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def is_proxy_link_valid(self):
        try:
            if self.proxy_cobrowse_io:
                total_sec = int(
                    (timezone.now() - self.generate_datetime).total_seconds())
                drop_link_expiry_time = self.agent.get_access_token_obj().get_proxy_config_obj().proxy_link_expire_time * 60
                if total_sec >= drop_link_expiry_time:
                    return False
                else:
                    return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on checking if is proxy link valid CobrowseDropLink %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return False

    def __str__(self):
        try:
            return str(self.key)
        except Exception:
            return "No link key"

    class Meta:
        verbose_name = "CobrowseDropLink"
        verbose_name_plural = "CobrowseDropLink"


class CobrowseSessionManagement(models.Model):

    key = models.CharField(max_length=100, null=False, blank=False)

    value = models.TextField(null=False, blank=False)

    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.key + " - " + self.value

    class Meta:
        verbose_name = "CobrowseSessionManagement"


class CobrowseAgentComment(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, help_text='Cobrowsing session object')

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text='agent who has given comments while closing session')

    agent_comments = models.TextField(
        null=True, blank=True, help_text='comments added by agent while closing session')

    agent_subcomments = models.TextField(
        null=True, blank=True, help_text='sub-comments added by agent while closing session')

    comment_desc = models.TextField(
        null=True, blank=True, default="", help_text='description for the comment')

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when comment has been given by agent')

    def __str__(self):
        return str(self.cobrowse_io.session_id) + " - " + str(self.agent.user.email)

    class Meta:
        verbose_name = 'CobrowseAgentComment'
        verbose_name_plural = 'CobrowseAgentComment'


class SystemAuditTrail(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, help_text='cobrowsing session', null=True, blank=True)

    cobrowse_access_token = models.ForeignKey(
        CobrowseAccessToken, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN, null=True, blank=True)

    category = models.CharField(max_length=100, null=False, blank=False)

    description = models.TextField(null=False, blank=False)

    datetime = models.DateTimeField(default=timezone.now)

    sender = models.ForeignKey(CobrowseAgent, on_delete=models.CASCADE, null=True, blank=True,
                               help_text='sender of audit trail. If this is None then sender is customer else it is from agent')

    def __str__(self):
        return str(self.category) + " - " + str(self.description)

    class Meta:
        verbose_name = 'SystemAuditTrail'
        verbose_name_plural = 'SystemAuditTrail'


class CobrowseChatHistory(models.Model):

    cobrowse_io = models.ForeignKey(CobrowseIO, on_delete=models.CASCADE, null=False,
                                    blank=False, help_text='session for which chat history has been saved')

    sender = models.ForeignKey(CobrowseAgent, on_delete=models.CASCADE, null=True, blank=True,
                               help_text='sender of message. If this is None then sender is customer else it is from agent')

    message = models.TextField(
        null=False, blank=False, help_text='message given user')

    chat_type = models.CharField(
        max_length=100, default="chat_message", choices=CHAT_TYPE)

    attachment_file_name = models.CharField(
        max_length=200, null=True, blank=True, help_text='contains name of attachment file')

    attachment = models.CharField(
        max_length=2000, null=True, blank=True, help_text='contains path to attachment file on agent side')

    datetime = models.DateTimeField(default=timezone.now)

    is_pii_data_masked = models.BooleanField(default=False)

    agent_profile_pic_source = models.CharField(
        max_length=500, default="", help_text='source of agent profile picture')

    def mask_customer_chat(self):
        try:
            if self.cobrowse_io.access_token and self.cobrowse_io.access_token.enable_masking_pii_data == True and self.cobrowse_io.is_archived == True:
                if self.chat_type == "chat_message":
                    self.message = hash_crucial_info_in_data(self.message)
                self.is_pii_data_masked = True
                self.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CobrowseChatHistory %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def __str__(self):
        return str(self.cobrowse_io.session_id) + " - " + str(self.message)

    def get_abs_attachment_url(self):
        try:
            if self.attachment == None:
                return None

            if isinstance(self.attachment, str) and self.attachment.startswith("/files/"):
                return settings.EASYCHAT_HOST_URL + self.attachment
            else:
                return self.attachment

        except Exception:
            return None

    class Meta:
        verbose_name = 'CobrowseChatHistory'
        verbose_name_plural = 'CobrowseChatHistory'


class CobrowsingFileAccessManagement(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    is_public = models.BooleanField(default=False)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True, help_text="Original name of file without adding any marker to make it unique")

    access_token = models.ForeignKey(
        'CobrowseAccessToken', default=None, null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when access management object is created')

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.is_public)

    def is_obj_time_limit_exceeded(self):
        try:
            import pytz
            curr_timezone = pytz.timezone(settings.TIME_ZONE)

            created_datetime = self.created_datetime.astimezone(
                curr_timezone)
            current_datetime = timezone.now().astimezone(curr_timezone)

            if (current_datetime - created_datetime).total_seconds() >= FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT * 60 * 60:
                return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("is_obj_time_limit_exceeded %s at %s",
                           str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return True

    class Meta:
        verbose_name = 'CobrowsingFileAccessManagement'
        verbose_name_plural = 'CobrowsingFileAccessManagement'


class SupportDocument(models.Model):

    file_name = models.CharField(max_length=2000, null=False, blank=True,
                                 help_text="file name which will displayed to agent and admin")

    file_path = models.CharField(max_length=2000, null=False, blank=True,
                                 help_text="file path where file is stored with name")

    file_type = models.CharField(
        max_length=20, null=False, blank=True, help_text="type of file")

    file_access_management_key = models.CharField(
        max_length=100, null=False, blank=True, help_text="CobrowsingFileAccessManagement key")

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text="admin or supervisor - file to be shown agent which are under this agent")

    added_on = models.DateTimeField(
        null=True, blank=True, default=timezone.now, help_text='datetime when given document was added')

    is_usable = models.BooleanField(
        default=True, help_text='is_usable true that files only will be shown to agent at cobrowsing time')

    is_deleted = models.BooleanField(
        default=False, help_text='marking as deleted rather then deleting it')

    def __str__(self):
        return str(self.file_name)

    class Meta:
        verbose_name = 'SupportDocument'
        verbose_name_plural = 'SupportDocument'


class CobrowseVideoConferencing(models.Model):

    meeting_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique meeting id for each video conferencing session')

    agent = models.ForeignKey(CobrowseAgent, on_delete=models.CASCADE, null=True, blank=True,
                              help_text='Agent who generated video conferencing link')

    support_meeting_agents = models.ManyToManyField(
        CobrowseAgent, blank=True, related_name="support_meeting_agents")

    full_name = models.CharField(max_length=100, null=True, blank=True)

    mobile_number = models.CharField(max_length=100, null=True, blank=True)

    email_id = models.EmailField(null=True, blank=True)

    meeting_description = models.CharField(
        max_length=2048, null=True, blank=True)

    meeting_start_date = models.DateField(null=True, blank=True)

    meeting_start_time = models.TimeField(null=True, blank=True)

    meeting_end_time = models.TimeField(null=True, blank=True)

    meeting_password = models.CharField(max_length=2048, null=True, blank=True)

    is_agent_connected = models.BooleanField(default=False)

    is_expired = models.BooleanField(default=False, db_index=True)

    is_cobrowsing_meeting = models.BooleanField(default=False)

    is_voip_meeting = models.BooleanField(default=False)

    feedback_rating = models.IntegerField(null=True, blank=True)

    feedback_comment = models.TextField(null=True, blank=True)

    agent_comments = models.TextField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            if self.agent and self.agent.get_access_token_obj().enable_masking_pii_data == True and self.is_expired == True:
                self.mobile_number = get_hashed_data(self.mobile_number)
                self.email_id = get_hashed_data(self.email_id)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CobrowseVideoConferencing %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        try:
            super(CobrowseVideoConferencing, self).save(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CobrowseVideoConferencing %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def __str__(self):
        return str(self.meeting_id) + " - " + str(self.full_name)

    class Meta:
        verbose_name = 'CobrowseVideoConferencing'
        verbose_name_plural = 'CobrowseVideoConferencing'


class CobrowseVideoAuditTrail(models.Model):

    cobrowse_video = models.ForeignKey(
        CobrowseVideoConferencing, on_delete=models.CASCADE, null=True, blank=True)

    cobrowse_forms = models.ManyToManyField(
        'CobrowseVideoConferencingForm', blank=True)

    agent_joined = models.DateTimeField(default=timezone.now)

    agent_end_time = models.DateTimeField(null=True, blank=True)

    meeting_ended = models.DateTimeField(default=timezone.now)

    agent_notes = models.TextField(null=True, blank=True)

    message_history = models.TextField(
        null=True, blank=True, help_text="Message history of the customer.")

    meeting_agents = models.ManyToManyField(
        CobrowseAgent, blank=True, help_text="Support agents who have joined the meeting")

    meeting_agents_invited = models.ManyToManyField(
        CobrowseAgent, blank=True, help_text="Support agents who were invited in the meeting", related_name="meeting_agents_invited")

    agent_recording_start_time = models.DateTimeField(default=timezone.now)

    meeting_recording = models.CharField(
        max_length=4096, null=True, blank=True)

    client_audio_recording = models.TextField(
        default="{\"items\":[]}", help_text="Client audio recording", null=True, blank=True)

    meeting_screenshot = models.TextField(
        default="{\"items\":[]}", help_text="Meeting Screenshot", null=True, blank=True)

    client_location_details = models.TextField(
        default="{\"items\":[]}", help_text="Client location details", null=True, blank=True)

    merged_filepath = models.CharField(
        max_length=4096, null=True, blank=True)

    is_merging_done = models.BooleanField(default=False)

    is_meeting_ended = models.BooleanField(default=False)

    is_pii_data_masked = models.BooleanField(default=False)

    meeting_initiated_by_list = (("agent", "Agent"),
                                 ("customer", "Customer"))

    meeting_initiated_by = models.CharField(
        choices=meeting_initiated_by_list, max_length=20, null=True, blank=True, help_text='This field tells who initiated the meeting')

    def mask_video_conferencing_data(self):
        try:
            if self.cobrowse_video and self.cobrowse_video.agent.get_access_token_obj().enable_masking_pii_data == True and self.cobrowse_video.is_expired == True:
                self.agent_notes = hash_crucial_info_in_data(
                    self.agent_notes)

                try:
                    try:
                        message_history = eval(self.message_history)
                    except Exception:
                        message_history = self.message_history

                    if message_history:
                        hashed_message_history = []
                        for message in message_history:
                            message = json.loads(message)
                            message["message"] = hash_crucial_info_in_data(
                                message["message"])

                            hashed_message_history.append(
                                json.dumps(message))

                        self.message_history = hashed_message_history
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error on saving CobrowseVideoAuditTrail %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                self.is_pii_data_masked = True
                self.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CobrowseVideoAuditTrail %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def get_meeting_chats(self):
        try:
            try:
                message_history = eval(self.message_history)
            except Exception:
                message_history = self.message_history

            if message_history:
                message_history_list = []
                for message in message_history:
                    message = json.loads(message)
                    message_history_list.append(message)
                return message_history_list
            else:
                return None

        except Exception:
            return None

    def get_meeting_duration(self):
        import time
        meeting_duration = 0
        try:
            meeting_duration = int((self.agent_end_time -
                                    self.agent_joined).total_seconds())

            meeting_duration = max(0, meeting_duration)
            meeting_duration = time.strftime(
                '%H:%M:%S', time.gmtime(meeting_duration))
        except Exception:
            meeting_duration = 0
        return meeting_duration

    def get_meeting_duration_in_seconds(self):
        import time
        meeting_duration = 0
        try:
            meeting_duration = int((self.agent_end_time -
                                    self.agent_joined).total_seconds())
        except Exception:
            meeting_duration = 0
        return meeting_duration

    def get_readable_meeting_duration(self):
        TIME_DURATION_UNITS = (
            ('week', 60 * 60 * 24 * 7),
            ('day', 60 * 60 * 24),
            ('hour', 60 * 60),
            ('min', 60),
            ('sec', 1)
        )
        import time
        meeting_duration = 0
        try:
            meeting_duration = int((self.agent_end_time -
                                    self.agent_joined).total_seconds())
        except Exception:
            meeting_duration = 0

        meeting_duration = max(0, meeting_duration)
        if meeting_duration < 60:
            return str(meeting_duration) + ' sec'
        meeting_duration = meeting_duration - (meeting_duration % 60)
        parts = []
        for unit, div in TIME_DURATION_UNITS:
            amount, meeting_duration = divmod(int(meeting_duration), div)
            if amount > 0:
                parts.append('{} {}{}'.format(
                    amount, unit, "" if amount == 1 else "s"))
        return ', '.join(parts)

    def get_meeting_agents(self):
        agents = []
        support_agents = self.meeting_agents.all()
        for agent in support_agents:
            agents.append(agent.user.username)
        return agents

    def get_meeting_invited_agents(self):
        try:
            agents = []
            invited_support_agents = self.meeting_agents_invited.all()
            for agent in invited_support_agents:
                agents.append(agent.user.username)
            return agents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_invited_agents %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    def get_meeting_forms(self):
        cobrowse_forms = self.cobrowse_forms.filter(is_deleted=False)
        return cobrowse_forms

    def get_client_location_details(self):
        try:
            client_location_details = json.loads(self.client_location_details)
            return client_location_details['items']
        except Exception:
            return []

    def get_meeting_screenshot(self):
        try:
            meeting_screenshot = json.loads(self.meeting_screenshot)
            return meeting_screenshot['items']
        except Exception:
            return []

    def get_meeting_screenshot_links(self):
        try:
            screenshot_list = []
            meeting_screenshot = self.get_meeting_screenshot()
            for screenshot_obj in meeting_screenshot:
                screenshot_id = screenshot_obj["screenshot"]
                screenshot_link = settings.EASYCHAT_HOST_URL + \
                    "/easy-assist/download-file/" + screenshot_id
                screenshot_list.append(screenshot_link)

            return screenshot_list
        except Exception:
            return []

    def get_meeting_main_primary_agent(self):
        try:
            main_primary_agent = None
            cobrowse_video_conf_obj = self.cobrowse_video
            if cobrowse_video_conf_obj:
                meeting_id = cobrowse_video_conf_obj.meeting_id
                cobrowse_io = CobrowseIO.objects.filter(
                    session_id=meeting_id).first()
                if cobrowse_io:
                    if cobrowse_io.main_primary_agent:
                        main_primary_agent = cobrowse_io.main_primary_agent.user.username

            return main_primary_agent
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_main_primary_agent %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def get_meeting_auto_assigned_agents(self):
        try:
            auto_assigned_agents = "-"
            cobrowse_video_conf_obj = self.cobrowse_video
            if cobrowse_video_conf_obj:
                meeting_id = cobrowse_video_conf_obj.meeting_id
                cobrowse_io = CobrowseIO.objects.filter(
                    session_id=meeting_id).first()
                if cobrowse_io:
                    if cobrowse_io.access_token.enable_auto_assign_unattended_lead:
                        if cobrowse_io.agents_assigned_list.all():
                            auto_assigned_agents = ""
                            for agent in cobrowse_io.agents_assigned_list.all():
                                auto_assigned_agents += agent.user.username + ", "
                            auto_assigned_agents = auto_assigned_agents[:-2]

            return auto_assigned_agents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_auto_assigned_agents %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def get_meeting_assigned_agents_list(self):
        try:
            assigned_agents_list = []
            cobrowse_video_conf_obj = self.cobrowse_video
            if cobrowse_video_conf_obj:
                meeting_id = cobrowse_video_conf_obj.meeting_id
                cobrowse_io = CobrowseIO.objects.filter(
                    session_id=meeting_id).first()
                if cobrowse_io and cobrowse_io.access_token.enable_auto_assign_unattended_lead:
                    assigned_agents_list = cobrowse_io.get_unattended_lead_transfer_audit_trail()

            return assigned_agents_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_assigned_agents_list %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return []

    def get_lead_initiated_by(self):
        try:
            lead_initiated_by = "-"
            cobrowse_video_conf_obj = self.cobrowse_video
            if cobrowse_video_conf_obj:
                meeting_id = cobrowse_video_conf_obj.meeting_id
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=meeting_id).first()
                if cobrowse_io_obj:
                    if cobrowse_io_obj.lead_initiated_by == 'floating_button':
                        lead_initiated_by = "Floating Button"
                    elif cobrowse_io_obj.lead_initiated_by == 'greeting_bubble':
                        lead_initiated_by = "Greeting Bubble"
                    elif cobrowse_io_obj.lead_initiated_by == 'icon':
                        lead_initiated_by = "Icon"
                    elif cobrowse_io_obj.lead_initiated_by == 'exit_intent':
                        lead_initiated_by = "Exit Intent"
                    elif cobrowse_io_obj.lead_initiated_by == 'inactivity_popup':
                        lead_initiated_by = "Inactivity Pop-up"

            return lead_initiated_by
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_lead_initiated_by %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def get_self_assign_time(self):
        try:
            self_assign_time = "-"
            cobrowse_video_conf_obj = self.cobrowse_video
            if cobrowse_video_conf_obj:
                meeting_id = cobrowse_video_conf_obj.meeting_id
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=meeting_id).first()
                if cobrowse_io_obj and cobrowse_io_obj.access_token.enable_request_in_queue:
                    self_assign_time = cobrowse_io_obj.get_self_assign_time()
            if not self_assign_time:
                self_assign_time = "-"
            return self_assign_time
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_self_assign_time %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def get_meeting_initiated_by(self):
        try:
            if self.meeting_initiated_by:
                if self.meeting_initiated_by == "agent":
                    return "Agent"
                elif self.meeting_initiated_by == "customer":
                    return "Customer"
                else:
                    return "-"
            else:
                return "-"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_initiated_by %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return "-"

    def __str__(self):
        return str(self.cobrowse_video.meeting_id) + " - " + str(self.cobrowse_video.full_name)

    class Meta:
        verbose_name = 'CobrowseVideoAuditTrail'
        verbose_name_plural = 'CobrowseVideoAuditTrail'


class CobrowseVideoConferencingForm(models.Model):

    form_name = models.CharField(max_length=100, null=True, blank=True)

    agents = models.ManyToManyField(
        CobrowseAgent, blank=True, help_text="Agents who have access to the forms")

    is_deleted = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.form_name

    class Meta:
        verbose_name = 'CobrowseVideoConferencingForm'
        verbose_name_plural = 'CobrowseVideoConferencingForm'

    def get_datetime(self):
        import pytz
        est = pytz.timezone(settings.TIME_ZONE)
        return self.updated_at.astimezone(est).strftime("%b %d %Y %I:%M %p")


class CobrowseVideoconferencingFormCategory(models.Model):

    form = models.ForeignKey('CobrowseVideoConferencingForm',
                             null=True, on_delete=models.CASCADE)

    title = models.CharField(max_length=250, null=False, blank=False)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.form.form_name + " - " + self.title

    class Meta:
        verbose_name = 'CobrowseVideoconferencingFormCategory'
        verbose_name_plural = 'CobrowseVideoconferencingFormCategories'


class CobrowseVideoConferencingFormElement(models.Model):

    form_category = models.ForeignKey('CobrowseVideoconferencingFormCategory',
                                      null=True, on_delete=models.CASCADE)

    element_type = models.CharField(
        max_length=100, null=True, blank=True, choices=FORM_INPUT_CHOICES)

    element_label = models.CharField(max_length=100, null=True, blank=True)

    element_choices = models.TextField(
        default="[]", null=True, blank=True)

    is_mandatory = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.form_category.form.form_name + " - " + self.form_category.title + " - " + self.element_label

    def get_element_choices(self):
        try:
            choices = json.loads(self.element_choices)
            return choices
        except Exception:
            return []

    class Meta:
        verbose_name = 'CobrowseVideoConferencingFormElement'
        verbose_name_plural = 'CobrowseVideoConferencingFormElements'


class CobrowseVideoConferencingFormData(models.Model):

    cobrowse_video = models.ForeignKey(
        CobrowseVideoConferencing, on_delete=models.CASCADE, null=True, blank=True)

    form_element = models.ForeignKey('CobrowseVideoConferencingFormElement',
                                     on_delete=models.CASCADE, null=True, blank=True)

    collected_values = models.TextField(
        default="[]", null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.cobrowse_video.meeting_id) + "-" + self.form_element.form_category.form.form_name + "-" + self.form_element.element_label

    def get_collected_values(self):
        try:
            collected_values = json.loads(self.collected_values)
            return collected_values
        except Exception:
            return []

    class Meta:
        verbose_name = 'CobrowseVideoConferencingFormEntry'
        verbose_name_plural = 'CobrowseVideoConferencingFormEntries'

    def get_datetime(self):
        import pytz
        est = pytz.timezone(settings.TIME_ZONE)
        return self.updated_at.astimezone(est).strftime("%b %d %Y %I:%M %p")


class NotificationManagement(models.Model):

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, help_text="notification is for this agent")

    cobrowse_io = models.ForeignKey(CobrowseIO, on_delete=models.SET_NULL, null=True,
                                    blank=True, default=None, help_text='notification generated for this session')

    product_name = models.CharField(max_length=1000, default="-", blank=True,
                                    help_text="This field stores the name of the product for which the notification is being sent.")

    notification_message = models.CharField(max_length=1000, default="-", blank=True,
                                            help_text="notification message")

    show_notification = models.BooleanField(
        default=True, help_text='want to show notification')

    datetime_notification_generated = models.DateTimeField(
        null=True, blank=True, default=timezone.now, help_text='datetime when notification is generated')

    datetime_notification_checked = models.DateTimeField(
        null=True, blank=True, default=None, help_text='notification sent to agent')

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.notification_message)

    class Meta:
        verbose_name = 'NotificationManagement'
        verbose_name_plural = 'NotificationManagement'


class LanguageSupport(models.Model):

    title = models.CharField(max_length=100, null=False, blank=False)

    index = models.IntegerField(
        default=0, help_text='index to decide relative position of languages')

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + str(self.index) + " -- " + str(self.is_deleted)

    class Meta:
        verbose_name = 'LanguageSupport'
        verbose_name_plural = 'LanguageSupports'


class ProductCategory(models.Model):

    title = models.CharField(max_length=250, null=False, blank=False)

    index = models.IntegerField(
        default=0, help_text='index to decide relative position of products')

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + str(self.index) + " -- " + str(self.is_deleted)

    class Meta:
        verbose_name = 'ProductCategory'
        verbose_name_plural = 'ProductCategory'


class CobrowseAgentOnlineAuditTrail(models.Model):

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, null=True, blank=True)

    last_online_start_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='start datetime when agent was last online')

    last_online_end_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='end datetime when agent was last online')

    idle_time = models.IntegerField(
        default=0, help_text='Total time in seconds when agent was online but not doing any session')

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.last_online_start_datetime) + " - " + str(self.last_online_end_datetime)

    class Meta:
        verbose_name = 'CobrowseAgentOnlineAuditTrail'
        verbose_name_plural = 'CobrowseAgentOnlineAuditTrail'


class CobrowseAgentWorkAuditTrail(models.Model):

    agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, null=True, blank=True)

    session_start_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='start datetime when agent start meeting or cobrowsing session')

    session_end_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='end datetime when agent leave meeting or cobrowsing session')

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.session_start_datetime) + " - " + str(self.session_end_datetime)

    class Meta:
        verbose_name = 'CobrowseAgentWorkAuditTrail'
        verbose_name_plural = 'CobrowseAgentWorkAuditTrail'


class EasyAssistVisitor(models.Model):

    visiting_date = models.DateField(
        null=True, blank=True, help_text='date when user visited the page')

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    visitor_count = models.IntegerField(default=1, help_text='visitor count')

    def __str__(self):
        return self.visiting_date

    class Meta:
        verbose_name = 'EasyAssistVisitor'
        verbose_name_plural = 'EasyAssistVisitors'


class CobrowseScreenRecordingAuditTrail(models.Model):

    agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                              on_delete=models.SET_NULL, help_text='agent assigned to client for cobrowsing')

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    recorded_file = models.CharField(
        max_length=2000, null=True, blank=True, help_text='contains path to recorded file')

    recording_started = models.DateTimeField(default=timezone.now)

    recording_ended = models.DateTimeField(default=timezone.now)

    is_recording_ended = models.BooleanField(default=False)

    is_expired = models.BooleanField(default=False)

    def get_screen_recording_duration(self):
        time = ""
        try:
            recording_duration = int((self.recording_ended -
                                      self.recording_started).total_seconds())
            hour = (recording_duration) // 3600
            rem = (recording_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            if sec != 0:
                time += str(sec) + "s"
        except Exception:
            pass

        return "0s" if time == "" else time

    def get_recording_expiration_time(self):
        days = "Today"
        try:
            recorded_days = (datetime.datetime.today().date() -
                             self.recording_started.date()).days
            if recorded_days >= int(self.cobrowse_io.access_token.recording_expires_in_days):
                days = "Today"
            else:
                days = self.cobrowse_io.access_token.recording_expires_in_days - recorded_days
        except Exception:
            pass

        return days

    def __str__(self):
        try:
            agent_username = str(self.agent.user.username)
        except Exception:
            agent_username = "-"
        return str(self.cobrowse_io.session_id) + " - " + str(agent_username)

    class Meta:
        verbose_name = 'CobrowseScreenRecordingAuditTrail'
        verbose_name_plural = 'CobrowseScreenRecordingAuditTrails'


class CobrowseCapturedLeadData(models.Model):

    primary_value = models.CharField(
        max_length=1000, null=True, blank=True, db_index=True)

    session_id = models.UUIDField(default=uuid.uuid4,
                                  editable=False, help_text='unique session id for each cobrowsing session')

    lead_request_datetime = models.DateTimeField(default=timezone.now)

    search_field = models.ForeignKey(CobrowseLeadHTMLField, blank=True, null=True,
                                     on_delete=models.CASCADE, help_text="On which the client have entered the data")

    is_active = models.BooleanField(
        default=False, help_text='bool: lead is active or not')

    agent_searched = models.BooleanField(
        default=False, help_text='bool: If this is set to True, it means that agent searched this lead using this objects primary value.')

    def __str__(self):
        return str(self.session_id)

    class Meta:
        verbose_name = 'CobrowseCapturedLeadData'
        verbose_name_plural = 'CobrowseCapturedLeadDatas'


class AppCobrowsingSessionManagement(models.Model):

    cobrowse_io = models.ForeignKey(CobrowseIO, on_delete=models.CASCADE, null=False,
                                    blank=False, help_text='session for which chat history has been saved')

    user_type = models.CharField(max_length=200, null=False, blank=False)

    user_alias = models.CharField(max_length=200, null=False, blank=False)

    user_token = models.CharField(
        max_length=2000, null=False, blank=False, unique=True, editable=False)

    start_datetime = models.DateTimeField(default=timezone.now)

    last_update_datetime = models.DateTimeField(default=timezone.now)

    is_closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        user_token = str(self.cobrowse_io.session_id) + "|" + self.user_alias
        self.user_token = hashlib.md5(user_token.encode()).hexdigest()
        super(AppCobrowsingSessionManagement, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user_alias) + " - " + str(self.cobrowse_io.session_id)

    class Meta:
        verbose_name = 'AppCobrowsingSessionManagement'
        verbose_name_plural = 'AppCobrowsingSessionManagement'


class EasyAssistExportDataRequest(models.Model):

    agent = models.ForeignKey(
        'CobrowseAgent', null=True, blank=True, on_delete=models.CASCADE)

    report_type = models.CharField(
        max_length=256, null=False, blank=False, choices=REPORT_TYPE_CHOICES)

    file_path = models.CharField(max_length=500, null=False, blank=False)

    export_request_datetime = models.DateTimeField(default=timezone.now)

    filter_param = models.TextField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.agent.user.username)

    class Meta:
        verbose_name = 'EasyAssistExportDataRequest'
        verbose_name_plural = 'EasyAssistExportDataRequest'


class CobrowsePageVisitCount(models.Model):

    cobrowse_access_token = models.ForeignKey(
        CobrowseAccessToken, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN, null=True, blank=True)

    page_title = models.CharField(
        max_length=2000, blank=True, help_text="Title of the page visited by the Client")

    page_url = models.CharField(
        max_length=2000, blank=True, help_text="Url of the page visted by the Client")

    page_visit_date = models.DateField(
        default=timezone.now, help_text='Date of visit to the page by the Client')

    page_count = models.IntegerField(
        default=0, help_text="Count of visits on that particular Page on a particular day")

    def __str__(self):
        return self.page_title

    class Meta:
        verbose_name = 'CobrowsePageVisitCount'
        verbose_name_plural = 'CobrowsePageVisitCount'


class CobrowseCustomSelectRemoveField(models.Model):

    key = models.CharField(max_length=200, null=False, blank=False)

    value = models.CharField(max_length=1000, null=False, blank=False)

    def __str__(self):
        return str(self.key) + " - " + str(self.value)

    class Meta:
        verbose_name = 'CobrowseCustomSelectRemoveField'
        verbose_name_plural = 'CobrowseCustomSelectRemoveFields'


class AssignTaskProcessor(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    function = models.TextField(
        default=ASSIGN_TAKS_PROCESSOR_CODE, null=True, blank=True, help_text="Function code")

    class Meta:
        verbose_name = "AssignTaskProcessor"
        verbose_name_plural = "AssignTaskProcessor"

    def __str__(self):
        return self.access_token.agent.user.username


class AssignTaskProcessorLogger(models.Model):

    agent = models.OneToOneField(CobrowseAgent, on_delete=models.CASCADE,
                                 unique=True, help_text=ADMIN_RESPONSIBLE_FOR_THE_SAME)

    function = models.TextField(
        null=True, blank=True, help_text="Function code")

    assign_task_process = models.ForeignKey(
        'AssignTaskProcessor', null=True, blank=True, on_delete=models.CASCADE)

    update_time = models.DateTimeField(
        null=True, blank=True, default=timezone.now)

    def __str__(self):
        return str(self.assign_task_process.access_token.key) + " - " + self.agent.user.username


class StaticFileChangeLogger(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.CASCADE, help_text=ADMIN_RESPONSIBLE_FOR_THE_SAME)

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    source_file_path = models.TextField(
        null=True, blank=True, help_text="Relative path of file which is changed")

    backup_file_path = models.TextField(
        null=True, blank=True, help_text="Saved file path")

    update_time = models.DateTimeField(
        null=True, blank=True, default=timezone.now)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.agent.user.username + " - " + str(self.update_time) + " - " + self.source_file_path + " - " + str(self.is_deleted)

    class Meta:
        verbose_name = 'StaticFileChangeLogger'
        verbose_name_plural = 'StaticFileChangeLoggers'


class CRMIntegrationModel(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    auth_token = models.CharField(max_length=100, null=True, blank=True, unique=True,
                                  help_text='Auto generated authorization token', db_index=True)

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when token was generated')

    is_expired = models.BooleanField(default=False)

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.CASCADE, help_text="Agent who created this object")

    def __str__(self):
        return self.auth_token + " - " + str(self.is_expired)

    def save(self, *args, **kwargs):

        if not self.auth_token:
            uuid_hex = uuid.uuid4().hex[: 16]
            auth_token = uuid_hex + ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=16))
            auth_token = auth_token.upper()
            self.auth_token = auth_token

        super(CRMIntegrationModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'CRMIntegrationModel'
        verbose_name_plural = 'CRMIntegrationModels'


class CRMCobrowseLoginToken(models.Model):

    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique token id for each login session')

    cobrowse_io = models.ForeignKey('CobrowseIO', null=True, blank=True, on_delete=models.SET_NULL,
                                    help_text='Cobrowse session object for which token is generated')

    cobrowse_drop_link = models.ForeignKey('CobrowseDropLink', null=True, blank=True,
                                           on_delete=models.SET_NULL, help_text='Agent who is requested the authenticate')

    meeting_io = models.ForeignKey("CobrowseVideoConferencing", null=True, blank=True,
                                   on_delete=models.SET_NULL, help_text='Meeting session object for which token is generated')

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'CRMCobrowseLoginToken'
        verbose_name_plural = 'CRMCobrowseLoginTokens'


class ChromeExtensionDetails(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when extension is created')

    extension_name = models.CharField(max_length=100, null=True, blank=True)

    deploy_links = models.TextField(null=True, blank=True)

    extension_path = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.extension_name

    class Meta:
        verbose_name = 'ChromeExtensionDetails'
        verbose_name_plural = 'ChromeExtensionDetails'


class EasyAssistBugReport(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL, help_text=ADMIN_RESPONSIBLE_FOR_THE_SAME)

    cobrowse_io = models.ForeignKey(
        CobrowseIO, null=True, blank=True, on_delete=models.SET_NULL, help_text='Cobrowsing session object')

    description = models.TextField(
        null=True, blank=True, help_text='description entred by agent')

    meta_data = models.TextField(
        null=True, blank=True, help_text='meta data - JSON format')

    files = models.TextField(
        null=True, blank=True, help_text='image/metadata/zip')

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when meta data is saved')

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'EasyAssistBugReport'
        verbose_name_plural = 'EasyAssistBugReports'


class CobrowseDateWiseInboundAnalytics(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL)

    date = models.DateField(
        default=timezone.now, help_text=DATE_WHEN_ANALYTICS_IS_SAVED)

    request_initiated = models.IntegerField(default=0)

    request_initiated_by_floating_button_icon = models.IntegerField(default=0)

    request_initiated_by_greeting_bubble = models.IntegerField(default=0)

    request_initiated_by_exit_intent = models.IntegerField(default=0)

    request_initiated_by_inactivity_popup = models.IntegerField(default=0)

    request_attended = models.IntegerField(default=0)

    request_unattended = models.IntegerField(default=0)

    customers_converted = models.IntegerField(default=0)

    customers_converted_by_url = models.IntegerField(default=0)

    declined_leads = models.IntegerField(default=0)

    followup_leads = models.IntegerField(default=0, help_text="No. of the followup leads assigned")

    request_not_initiated = models.IntegerField(default=0)

    group_cobrowse_request_initiated = models.IntegerField(default=0)

    group_cobrowse_request_received = models.IntegerField(default=0)

    group_cobrowse_request_connected = models.IntegerField(default=0)

    transfer_requests_received = models.IntegerField(default=0)

    transfer_requests_connected = models.IntegerField(default=0)

    transfer_requests_rejected = models.IntegerField(default=0)

    total_session_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=TOTAL_COBROWSING_SESSION_DURATION)

    attended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for attended leads (sec)")

    unattended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for unattended leads (sec)")

    request_assistance_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for customer requesting assistance (sec)")

    self_assign_sessions = models.IntegerField(default=0, help_text="Total Sessions self assigned by the agent")

    total_self_assign_time = models.IntegerField(default=0, help_text="Total self assign time by the agent ")

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.date)

    class Meta:
        verbose_name = 'CobrowseDateWiseInboundAnalytics'
        verbose_name_plural = 'CobrowseDateWiseInboundAnalytics'


class CobrowseDateWiseOutboundAnalytics(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL)

    date = models.DateField(
        default=timezone.now, help_text=DATE_WHEN_ANALYTICS_IS_SAVED)

    captured_leads = models.IntegerField(default=0)

    searched_leads = models.IntegerField(default=0)

    request_attended = models.IntegerField(default=0)

    customers_converted = models.IntegerField(default=0)

    customers_converted_by_url = models.IntegerField(default=0)

    request_unattended = models.IntegerField(default=0)

    requests_denied_by_customers = models.IntegerField(default=0)

    group_cobrowse_request_initiated = models.IntegerField(default=0)

    group_cobrowse_request_received = models.IntegerField(default=0)

    group_cobrowse_request_connected = models.IntegerField(default=0)

    transfer_requests_received = models.IntegerField(default=0)

    transfer_requests_connected = models.IntegerField(default=0)

    transfer_requests_rejected = models.IntegerField(default=0)

    total_session_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=TOTAL_COBROWSING_SESSION_DURATION)

    attended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for attended leads (sec)")

    unattended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for unattended leads (sec)")

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.date)

    class Meta:
        verbose_name = 'CobrowseDateWiseOutboundAnalytics'
        verbose_name_plural = 'CobrowseDateWiseOutboundAnalytics'


class CobrowseDateWiseOutboundDroplinkAnalytics(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL)

    date = models.DateField(
        default=timezone.now, help_text=DATE_WHEN_ANALYTICS_IS_SAVED)

    request_initiated = models.IntegerField(default=0)

    declined_leads = models.IntegerField(default=0)

    request_attended = models.IntegerField(default=0)

    customers_converted = models.IntegerField(default=0)

    customers_converted_by_url = models.IntegerField(default=0)

    request_unattended = models.IntegerField(default=0)

    total_session_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=TOTAL_COBROWSING_SESSION_DURATION)
    
    total_droplinks_generated = models.IntegerField(default=0, help_text="Total drop links generated by agent")

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.date)

    class Meta:
        verbose_name = 'CobrowseDateWiseOutboundDroplinkAnalytics'
        verbose_name_plural = 'CobrowseDateWiseOutboundDroplinkAnalytics'


class CobrowseDateWiseReverseAnalytics(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL)

    date = models.DateField(
        default=timezone.now, help_text=DATE_WHEN_ANALYTICS_IS_SAVED)

    links_generated = models.IntegerField(default=0)

    request_attended = models.IntegerField(default=0)

    customers_converted = models.IntegerField(default=0)

    customers_converted_by_url = models.IntegerField(default=0)

    total_session_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=TOTAL_COBROWSING_SESSION_DURATION)

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.date)

    class Meta:
        verbose_name = 'CobrowseDateWiseReverseAnalytics'
        verbose_name_plural = 'CobrowseDateWiseReverseAnalytics'


class CobrowseMailerAnalyticsProfile(models.Model):

    name = models.CharField(
        max_length=256, null=True, blank=True)

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mailer anlytics profile is created')

    email_address = models.TextField(default="[]", null=True, blank=True)

    email_subject = models.TextField(
        default=EMAIL_SUBJECT, null=True, blank=True)

    include_graphs = models.BooleanField(default=True)

    analytics_graph = models.ForeignKey(
        'CobrowseMailerAnalyticsGraph', null=True, blank=True, on_delete=models.SET_NULL)

    include_tables = models.BooleanField(default=True)

    analytics_table = models.ForeignKey(
        'CobrowseMailerAnalyticsTable', null=True, blank=True, on_delete=models.SET_NULL)

    include_attachment = models.BooleanField(default=True)

    include_mailer_analytics_attachment = models.BooleanField(default=True)

    analytics_attachment = models.ForeignKey(
        'CobrowseMailerAnalyticsAttachment', null=True, blank=True, on_delete=models.SET_NULL)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsProfile'
        verbose_name_plural = 'CobrowseMailerAnalyticsProfile'


class CobrowseMailerProfileStaticEmailAuditTrail(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    email_sent_count = models.IntegerField(
        default=STATIC_EMAIL_TRIGGER_COUNT, help_text='Number of times static email has been sent to the user')

    last_static_email_sent_time = models.DateTimeField(
        default=timezone.now, help_text='Datetime when static email for the analytics profile is triggered')

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'CobrowseMailerProfileStaticEmailAuditTrail'
        verbose_name_plural = 'CobrowseMailerProfileStaticEmailAuditTrail'


class CobrowseMailerAnalyticsGraph(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    records = models.TextField(
        default="[]", null=True, blank=True)

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsGraph'
        verbose_name_plural = 'CobrowseMailerAnalyticsGraph'


class CobrowseMailerAnalyticsTable(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    count_variation = models.TextField(
        default="[]", null=True, blank=True)

    records = models.TextField(
        default="[]", null=True, blank=True)

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsTable'
        verbose_name_plural = 'CobrowseMailerAnalyticsTable'


class CobrowseMailerAnalyticsAttachment(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    records = models.TextField(default="[]", null=True, blank=True)

    use_single_file = models.BooleanField(default=True)

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsAttachment'
        verbose_name_plural = 'CobrowseMailerAnalyticsAttachment'


class CobrowseMailerAnalyticsCalendar(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    months = models.TextField(null=True, blank=True)

    days = models.TextField(null=True, blank=True)

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsCalendar'
        verbose_name_plural = 'CobrowseMailerAnalyticsCalendar'


class CobrowseMailerAnalyticsAuditTrail(models.Model):

    profile = models.ForeignKey(
        'CobrowseMailerAnalyticsProfile', null=True, blank=True, on_delete=models.SET_NULL)

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mailer analytics sent')

    sent_days_count = models.TextField(null=True, blank=True)

    def __str__(self):
        profile_name = DELETED_PROFILE
        if self.profile:
            profile_name = self.profile.name
        return profile_name + " - " + str(self.sent_days_count) + ' - ' + str(self.datetime)

    class Meta:
        verbose_name = 'CobrowseMailerAnalyticsAuditTrail'
        verbose_name_plural = 'CobrowseMailerAnalyticsAuditTrail'


class CobrowseSandboxUser(models.Model):

    user = models.OneToOneField(
        "EasyChatApp.User", on_delete=models.CASCADE, primary_key=True)

    password = models.TextField(null=True, blank=True)

    create_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the sandbox account was created')

    enable_cobrowsing = models.BooleanField(default=False)

    enable_inbound = models.BooleanField(default=False)

    enable_outbound = models.BooleanField(default=False)

    enable_reverse_cobrowsing = models.BooleanField(default=False)

    enable_video_meeting = models.BooleanField(default=False)

    is_expired = models.BooleanField(default=False)

    expire_date = models.DateField(
        null=True, blank=True, help_text='Datetime when sandbox user Credentials will expire')

    last_update_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text='Datetime when sandbox user Credentials has been updated')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'CobrowseSandboxUser'
        verbose_name_plural = 'CobrowseSandboxUsers'


class CobrowseIOInvitedAgentsDetails(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    support_agents_invited = models.ManyToManyField(
        CobrowseAgent, blank=True, related_name="support_agents_invited", help_text="Stores the list of support agents that have been invited for the particular cobrowse session")

    support_agents_joined = models.ManyToManyField(
        CobrowseAgent, blank=True, related_name="support_agents_joined", help_text="Stores the list of support agents that have joined the particular cobrowse session")

    def __str__(self):
        str_value = "Session ID - " + str(self.cobrowse_io.session_id)
        return str_value

    class Meta:
        verbose_name = 'CobrowseIOInvitedAgentsDetails'
        verbose_name_plural = 'CobrowseIOInvitedAgentsDetails'


class CobrowseCalendar(models.Model):

    event_type = models.CharField(max_length=1,
                                  default="1",
                                  null=False,
                                  blank=False,
                                  choices=EASYASSIST_EVENT_TYPE)
    event_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time of the event.")
    description = models.CharField(max_length=100, default="-")
    auto_response = models.TextField(
        default="Thank you, we have captured your details. We will contact you shortly", null=True, blank=True, help_text="this text will be shown to customer in case of holiday.")
    created_by = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="creator", help_text="CobrowseAgent(Admin/Supervisor)")
    modified_by = models.ForeignKey('CobrowseAgent', null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="modifier", help_text="CobrowseAgent(Admin/Supervisor)")
    created_at = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user created this event.")
    modified_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time, when this event got modified.")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "CobrowseCalendar"
        verbose_name_plural = "CobrowseCalendars"

    def __str__(self):
        return self.description


class AgentDetailsAPIProcessor(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    function = models.TextField(
        default=AGENT_DETAILS_PROCESSOR_CODE, null=True, blank=True, help_text="Comprises of the code to fetch agent details via the written API")

    class Meta:
        verbose_name = "AgentDetailsProcessor"
        verbose_name_plural = "AgentDetailsProcessors"

    def __str__(self):
        return self.access_token.agent.user.username


# This model is used to enable/disable API integration for EasyAssistApp
class EasyAssistAPIIntegrationManager(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    enable_agent_details_api = models.BooleanField(
        default=True, help_text="If true, api for fetching additional details of agent will be enabled.")

    class Meta:
        verbose_name = "EasyAssistAPIIntegrationManager"
        verbose_name_plural = "EasyAssistAPIIntegrationManagers"

    def __str__(self):
        return self.access_token.agent.user.username


class UnattendedLeadTransferAuditTrail(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text="Cobrowsing session object")

    auto_assigned_agent = models.ForeignKey(
        CobrowseAgent, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text="Stores the agent who was assigned the CobrowseIO lead")

    auto_assign_datetime = models.DateTimeField(
        default=timezone.now, blank=True, help_text="Corressponds to the datetime of when the agent was assigned the lead")

    def __str__(self):
        str_value = "Session ID - " + str(self.cobrowse_io.session_id)
        return str_value

    class Meta:
        verbose_name = 'UnattendedLeadTransferAuditTrail'
        verbose_name_plural = 'UnattendedLeadTransferAuditTrail'


class CobrowseIOTransferredAgentsLogs(models.Model):

    cobrowse_io = models.ForeignKey(
        CobrowseIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    transferred_agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                                          on_delete=models.SET_NULL, help_text='agent assigned to client for cobrowsing')

    inviting_agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name="iniviting_agent", help_text='inviting agent in cobrowsing')

    cobrowse_request_type = models.CharField(
        choices=COBROWSE_REQUEST_TYPE, max_length=20, null=False, default="", blank=True, help_text='Whether the lead request is from invited agent or from transferred agent')

    log_request_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when lead transferred')

    invited_status = models.CharField(
        max_length=20, null=False, default="", blank=True, help_text='status of invited agent')

    transferred_status = models.CharField(max_length=256,
                                          null=False,
                                          blank=True,
                                          default="",
                                          choices=TRANSFERRED_LEAD_STATUS)

    def __str__(self):
        str_value = "Session ID - " + str(self.cobrowse_io.session_id)
        return str_value

    class Meta:
        verbose_name = 'CobrowseIOTransferredAgentsLogs'
        verbose_name_plural = 'CobrowseIOTransferredAgentsLogs'


class ProxyCobrowseIO(models.Model):

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique session id for each cobrowsing session')

    client_page_link = models.CharField(max_length=1000, null=True, blank=True,
                                        help_text='active webpage url where client is filling the form', db_index=True)

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    key_generation_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text='Time at which proxy key is created.')

    def save(self, *args, **kwargs):
        try:
            super(ProxyCobrowseIO, self).save(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving ProxyCobrowseIO %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    def is_link_valid(self):
        try:
            total_sec = int(
                (timezone.now() - self.key_generation_datetime).total_seconds())
            link_expire_time = self.access_token.get_proxy_config_obj().proxy_link_expire_time * 60
            cobrowse_io = CobrowseIO.objects.filter(proxy_key_list__in=[self.session_id]).first()
            if total_sec > link_expire_time:
                return False
            if cobrowse_io and cobrowse_io.is_archived:
                return False
            else:
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on checking if is_link_valid %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return False

    def __str__(self):
        try:
            return str(self.session_id)
        except Exception:
            return "No session"

    class Meta:
        verbose_name = 'ProxyCobrowseIO'
        verbose_name_plural = 'ProxyCobrowseIO'


class EasyAssistCronjobTracker(models.Model):

    cronjob_id = models.CharField(max_length=100, null=True, blank=True,
                                  help_text='a unique ID of the cronjob being executed')

    creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the cronjob tracker object was created')
    
    def __str__(self):
        try:
            return str(self.cronjob_id)
        except Exception:
            return "-"

    '''
    This function is used only for checking whether the object created for 
    the schedular has expired or not. It is not used in the case of cronjobs.
    '''
    
    def is_object_expired(self):
        try:
            expiry_time_limit_in_seconds = CRONJOB_TRACKER_EXPIRY_TIME_LIMIT * 60
            total_time_elapsed = int((timezone.now() - self.creation_datetime).total_seconds())
            if total_time_elapsed >= expiry_time_limit_in_seconds:
                return True

            return False
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in EasyAssistCronjobTracker is_object_expired method %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return False

    class Meta:
        verbose_name = 'EasyAssistCronjobTracker'
        verbose_name_plural = 'EasyAssistCronjobTracker'


class EasyAssistPopupConfigurations(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    enable_url_based_inactivity_popup = models.BooleanField(
        default=False, help_text="This boolean shows whether enabling of customer inactivity popup only in specific URL's")

    inactivity_popup_urls = models.TextField(
        default="[]", null=True, blank=True, help_text="The Customer Inactivity popup works only for the URLs which were defined in this field.")

    enable_url_based_exit_intent_popup = models.BooleanField(
        default=False, help_text="This boolean shows whether enabling of Exit Intent only in specific URL's")

    exit_intent_popup_urls = models.TextField(
        default="[]", null=True, blank=True, help_text="The Exit Intent works only for the URLs which were defined in this field.")

    class Meta:
        verbose_name = 'EasyAssistPopupConfigurations'
        verbose_name_plural = 'EasyAssistPopupConfigurations'


class LiveChatCannedResponse(models.Model):

    agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                              on_delete=models.CASCADE, help_text='Agent who have created the responses')

    keyword = models.CharField(
        max_length=100, null=True, blank=True, default="", help_text="Keyword for canned response.")

    response = models.TextField(
        default="", null=True, blank=True, help_text="Response of given canned title.")

    is_deleted = models.BooleanField(
        default=False, help_text="Boolean to check whether canned response is deleted or not.")

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)
    
    def name(self):
        return self.keyword

    class Meta:
        verbose_name = "LiveChatCannedResponse"
        verbose_name_plural = "LiveChatCannedResponses"

    def save(self, *args, **kwargs):
        super(LiveChatCannedResponse, self).save(*args, **kwargs)


class AgentFrequentLiveChatCannedResponses(models.Model):

    agent = models.ForeignKey(CobrowseAgent, null=True, blank=True,
                              on_delete=models.CASCADE, help_text='Agent who have used canned response')

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)
        
    canned_response = models.ForeignKey(LiveChatCannedResponse, null=True, blank=True,
                                        on_delete=models.CASCADE, help_text='canned Response used by agent')

    frequency = models.IntegerField(
        default=1, help_text="Number of time response is used during livechat in cobrowsing")

    def name(self):
        return self.keyword

    class Meta:
        verbose_name = "AgentFrequentLiveChatCannedResponses"
        verbose_name_plural = "AgentFrequentLiveChatCannedResponses"

    def save(self, *args, **kwargs):
        super(AgentFrequentLiveChatCannedResponses, self).save(*args, **kwargs)


class ProxyCobrowseConfig(models.Model):

    access_token = models.ForeignKey(
        'CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE, help_text=COBROWSING_ACCESS_TOKEN)

    enable_proxy_cobrowsing = models.BooleanField(
        default=False, help_text="Enabling this will allow agents to do proxy cobrowsing.")

    proxy_link_expire_time = models.IntegerField(default=60,
                                                 help_text='generated proxy cobrowse link expiry time [in minutes]')

    class Meta:
        verbose_name = "ProxyCobrowseConfig"
        verbose_name_plural = "ProxyCobrowseConfig"


class CobrowseDateWiseOutboundProxyAnalytics(models.Model):

    agent = models.ForeignKey('CobrowseAgent', null=True, blank=True,
                              on_delete=models.SET_NULL, help_text='Agent whose data is being stored')

    date = models.DateField(
        default=timezone.now, help_text=DATE_WHEN_ANALYTICS_IS_SAVED)

    links_generated = models.IntegerField(
        default=0, help_text='No of proxy links genereated by the agent')

    customers_joined = models.IntegerField(
        default=0, help_text='No of the customers joined the session')

    request_attended = models.IntegerField(
        default=0, help_text='No of the request attended by the agent')

    customers_converted = models.IntegerField(
        default=0, help_text='No of the customers converted successfully')

    customers_converted_by_url = models.IntegerField(
        default=0, help_text='No of the customers successfully converted through url')

    request_unattended = models.IntegerField(
        default=0, help_text='No of the requests unattended')

    group_cobrowse_request_initiated = models.IntegerField(
        default=0, help_text='No of the requests initaited for invited agents')

    group_cobrowse_request_received = models.IntegerField(
        default=0, help_text='No of the requests received for support agent')

    group_cobrowse_request_connected = models.IntegerField(
        default=0, help_text='No of the requests connected for support agent')

    transfer_requests_received = models.IntegerField(
        default=0, help_text='No of the transfer requests received')

    transfer_requests_connected = models.IntegerField(
        default=0, help_text='No of the transfer requests connected')

    transfer_requests_rejected = models.IntegerField(
        default=0, help_text='No of the transfer requests rejected')

    total_session_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text=TOTAL_COBROWSING_SESSION_DURATION)

    attended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for attended leads (sec)")

    unattended_leads_total_wait_time = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text="Total waiting time for unattended leads (sec)")

    repeated_customers = models.IntegerField(
        default=0, help_text='No of the customers whose attended session more then one')

    unique_customers = models.IntegerField(
        default=0, help_text='No of the customers who attended the session only once')

    def __str__(self):
        return str(self.agent.user.username) + " - " + str(self.date)

    class Meta:
        verbose_name = 'CobrowseDateWiseOutboundProxyAnalytics'
        verbose_name_plural = 'CobrowseDateWiseOutboundProxyAnalytics'
