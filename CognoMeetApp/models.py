from django.db import models
from CognoMeetApp.constants import *
from django.utils import timezone
from django.db.models import Q
from CognoMeetApp.utils import hash_crucial_info_in_data
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import uuid
import logging
import sys
import json
import pytz

logger = logging.getLogger(__name__)


class CognoMeetAgent(models.Model):
    user = models.OneToOneField(
        USER, on_delete=models.CASCADE, primary_key=True)

    role = models.CharField(max_length=256, null=False,
                            blank=False, choices=USER_CHOICES)

    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    agent_creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the agent was created')

    agents = models.ManyToManyField('CognoMeetAgent', blank=True)

    is_active = models.BooleanField(default=False)

    is_account_active = models.BooleanField(default=True)

    is_meeting_active = models.BooleanField(default=False)

    access_token = models.ForeignKey(
        'CognoMeetAccessToken', on_delete=models.CASCADE, help_text=COGNOMEET_ACCESS_TOKEN, default=None, null=True, blank=True)

    def name(self):
        return self.user.username

    def __str__(self):
        return self.name()

    def get_access_token_obj(self):
        try:
            if self.role == "admin":
                return CognoMeetAccessToken.objects.get(agent=self)
            elif self.role == "supervisor":
                return CognoMeetAccessToken.objects.get(agent=CognoMeetAgent.objects.filter(agents__pk=self.pk).exclude(role="admin_ally")[0])
            elif self.role == "admin_ally":
                return CognoMeetAccessToken.objects.get(agent=CognoMeetAgent.objects.filter(agents__pk=self.pk).exclude(role="admin_ally")[0])
            else:
                parent_user = self
                try:
                    parent_user = CognoMeetAgent.objects.filter(
                        agents__pk=self.pk).exclude(Q(pk=self.pk) | Q(role="admin_ally"))[0]
                    try:
                        second_parent = CognoMeetAgent.objects.filter(
                            agents__pk=parent_user.pk).exclude(Q(pk=parent_user.pk) | Q(role="admin_ally"))[0]
                        return CognoMeetAccessToken.objects.get(agent=second_parent)
                    except Exception:
                        return CognoMeetAccessToken.objects.get(agent=parent_user)
                except Exception:
                    return CognoMeetAccessToken.objects.get(agent=self)
        except Exception:
            return None

    class Meta:
        verbose_name = 'CognoMeetAgent'
        verbose_name_plural = 'CognoMeetAgents'


@receiver(post_save, sender=CognoMeetAgent)
def create_cognomeet_access_token(sender, instance, **kwargs):
    if instance.role == "admin" and not kwargs["raw"]:
        cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(
            agent=instance).first()
        if not cognomeet_access_token_obj:
            cognomeet_access_token_obj = CognoMeetAccessToken.objects.create(
                agent=instance)
            if not CognoMeetTimers.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj).first():
                CognoMeetTimers.objects.create(
                    cogno_meet_access_token=cognomeet_access_token_obj)
            if not CognoMeetConfig.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj).first():
                CognoMeetConfig.objects.create(
                    cogno_meet_access_token=cognomeet_access_token_obj)
            instance.access_token = cognomeet_access_token_obj
            instance.save()


class CognoMeetAccessToken(models.Model):
    key = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    agent = models.OneToOneField(
        CognoMeetAgent, on_delete=models.CASCADE, unique=True, help_text="The admin agent of this access token")

    enable_screen_capture = models.BooleanField(
        default=True, help_text='If enabled agents can take a screenshot of the meet screen')

    enable_invite_agent = models.BooleanField(
        default=True, help_text='If enabled a help section gets displayed inside the meet interface, from there agents can invite other online agents')

    send_mail_to_invite_people = models.BooleanField(
        default=True, help_text='Mail will be sent to the invited people in enabled')

    show_lobby_page = models.BooleanField(
        default=True, help_text='If enabled customers have to wait in a lobby before agents allow them to join the meeting')

    ask_password = models.BooleanField(
        default=True, help_text='If enabled participants will be asked password for joining the meet')

    enable_time_duration = models.BooleanField(
        default=False, help_text='If enabled Admin can specify the maximum time duration a meeting can be scheduled for')

    max_time_duration = models.IntegerField(
        default=60, help_text='Max time duration for which meeting can be scheduled for [in minutes]')

    no_agent_permit_meeting_toast = models.BooleanField(
        default=True, help_text='If enabled the customer while waiting in the lobby gets displayed with a timer and a message that can be configured from the admin console')

    no_agent_permit_meeting_toast_time = models.IntegerField(
        default=1, help_text='Timer to be shown to the customer while in waiting lobby if no_agent_permit_meeting_toast is emabled [in minutes]')

    no_agent_permit_meeting_toast_text = models.TextField(
        default=NO_AGENT_PERMIT_MEETING_TOAST_TEXT, null=True, blank=True, help_text='Text to display at the waiting page')

    meeting_background_color = models.CharField(
        null=True, blank=True, max_length=100, default="#1A1A1A", help_text='Background color of the meeting')

    enable_feedback_in_meeting = models.BooleanField(
        default=True, help_text='Displays feedback modal to customers once call ends or the agent leaves, or the customer is removed from the call')

    meeting_default_password = models.CharField(
        max_length=2048, default="", null=True, blank=True)

    enable_auto_recording = models.BooleanField(
        default=False, help_text='records all types of meetings from the start to the end')

    enable_screen_sharing = models.BooleanField(
        default=True, help_text='If enabled a screen sharing option must be visible on the video calling interface')

    enable_meeting_chat = models.BooleanField(
        default=True, help_text='If enabled a chat option must be visible on the meeting interface')

    enable_pii_masking = models.BooleanField(
        default=True, help_text="If enabled, PII data is masked.")

    def __str__(self):
        return str(self.key) + " - " + str(self.agent.user.username)

    def get_cognomeet_timer_config_object(self):
        try:
            cognomeet_timer_config_obj = CognoMeetTimers.objects.filter(
                cogno_meet_access_token=self).first()
            if not cognomeet_timer_config_obj:
                cognomeet_timer_config_obj = CognoMeetTimers.objects.create(
                    cogno_meet_access_token=self)
            return cognomeet_timer_config_obj
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_cognomeet_timer_config_object %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return None

    def get_cognomeet_config_object(self):
        try:
            cognomeet_config_obj = CognoMeetConfig.objects.filter(
                cogno_meet_access_token=self).first()
            if not cognomeet_config_obj:
                cognomeet_config_obj = CognoMeetConfig.objects.create(
                    cogno_meet_access_token=self)
            return cognomeet_config_obj
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_cognomeet_config_object %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return None

    class Meta:
        verbose_name = 'CognoMeetAccessToken'
        verbose_name_plural = 'CognoMeetAccessToken'


class CognoMeetConfig(models.Model):
    organization_id = models.TextField(default=COGNO_MEET_ORGANIZATION_ID)

    api_key = models.TextField(default=COGNO_MEET_API_KEY)

    base_url = models.TextField(
        default=COGNO_MEET_BASE_URL, help_text="Base URL for v1 APIs")

    base_url_v2 = models.TextField(
        default=COGNO_MEET_BASE_URL_V2, help_text="Base URL for v2 APIs")

    api_timeout_time = models.IntegerField(default=DEFAULT_API_TIMEOUT_TIME)

    maximum_participants_limit = models.IntegerField(default=MAXIMUM_PARTICIPANTS_LIMIT,
                                                     help_text="The maximum number of participants allowed in a meeting.")

    cogno_meet_access_token = models.ForeignKey(
        'CognoMeetAccessToken', on_delete=models.CASCADE, help_text=COGNOMEET_ACCESS_TOKEN)

    class Meta:
        verbose_name = 'CognoMeetConfig'
        verbose_name_plural = 'CognoMeetConfig'

    def __str__(self):
        return "CognoMeetConfig - " + str(self.cogno_meet_access_token)


class CognoMeetTimers(models.Model):

    common_inactivity_timer = models.IntegerField(
        default=COMMON_INACTIVITY_TIMER, help_text="If there is no update from the participants of the meeting then the meeting would be expired after this timer gets exhausted (in mins)")

    cogno_meet_access_token = models.ForeignKey(
        'CognoMeetAccessToken', on_delete=models.CASCADE, help_text=COGNOMEET_ACCESS_TOKEN)

    class Meta:
        verbose_name = 'CognoMeetTimers'
        verbose_name_plural = 'CognoMeetTimers'

    def __str__(self):
        return "CognoMeetTimers - " + str(self.cogno_meet_access_token)


class CognoMeetIO(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique session id for each CognoMeet session')

    meeting_id = models.TextField(
        null=True, blank=True, help_text='meeting_id returned from Dyte')

    meeting_room_name = models.TextField(
        null=True, blank=True, help_text='room_name returned from Dyte')

    meeting_title = models.TextField(
        null=True, blank=True, help_text='Title of the meeting')

    # TODO: Sepateate out date and time
    meeting_request_creation_datetime = models.DateTimeField(
        null=True, blank=True, default=timezone.now, help_text='Datetime of when the meeting creation request was initiated')

    customer_name = models.CharField(
        max_length=1000, null=True, blank=True)

    customer_mobile = models.CharField(
        max_length=1000, null=True, blank=True)

    customer_email = models.CharField(
        max_length=1000, null=True, blank=True)

    meeting_password = models.CharField(max_length=2048, null=True, blank=True)

    meeting_start_date = models.DateField(null=True, blank=True)

    meeting_start_time = models.TimeField(null=True, blank=True)

    meeting_end_time = models.TimeField(null=True, blank=True)

    meeting_status = models.CharField(
        max_length=200, null=False, blank=False, choices=MEETING_STATUS)

    is_meeting_expired = models.BooleanField(
        default=False, help_text='Meeting will expire when last participant will leave the meet')

    agent_update_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='Stores the latest update datetime from the agent')

    customer_update_datetime = models.DateTimeField(
        null=True, blank=True, default=None, help_text='Stores the latest update datetime from the customer')

    cogno_meet_access_token = models.ForeignKey(
        'CognoMeetAccessToken', on_delete=models.CASCADE, help_text=COGNOMEET_ACCESS_TOKEN)

    cogno_meet_agent = models.ForeignKey(
        'CognoMeetAgent', null=False, blank=False, on_delete=models.CASCADE)

    support_meeting_agents = models.ManyToManyField(
        'CognoMeetAgent', blank=True, related_name="support_meeting_agents")

    is_meeting_recording_fetched = models.BooleanField(
        default=False, help_text="Tells if the meeting recording was fetched or not")

    def __str__(self):
        try:
            return str(self.session_id)
        except Exception:
            return "No session"

    def is_agent_inactivity_threshold_exceeded(self):
        try:
            inactivity_timer_mins = self.cogno_meet_access_token.get_cognomeet_timer_config_object(
            ).common_inactivity_timer
            inactivity_timer_secs = inactivity_timer_mins * 60
            time_since_last_update = int(
                (timezone.now() - self.agent_update_datetime).total_seconds())
            if time_since_last_update >= inactivity_timer_secs:
                return True
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_agent_inactivity_threshold_exceeded %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return False

    def is_customer_inactivity_threshold_exceeded(self):
        try:
            inactivity_timer_mins = self.cogno_meet_access_token.get_cognomeet_timer_config_object(
            ).common_inactivity_timer
            inactivity_timer_secs = inactivity_timer_mins * 60
            time_since_last_update = int(
                (timezone.now() - self.customer_update_datetime).total_seconds())
            if time_since_last_update >= inactivity_timer_secs:
                return True
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error is_customer_inactivity_threshold_exceeded %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return False

    class Meta:
        verbose_name = 'CognoMeetIO'
        verbose_name_plural = 'CognoMeetIO'


class CognoMeetRecording(models.Model):
    cogno_meet_io = models.ForeignKey(
        'CognoMeetIO', null=True, blank=False, on_delete=models.CASCADE)

    external_meeting_recording_url = models.TextField(null=True, blank=True,
                                                      default="", help_text="This consists of the meeting URL received from Dyte")

    file_access_management = models.ForeignKey(
        'CognoMeetFileAccessManagement', null=True, blank=False, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cogno_meet_io.session_id) + '-' + str(self.cogno_meet_io.cogno_meet_agent.name())

    class Meta:
        verbose_name = 'CognoMeetRecording'
        verbose_name_plural = 'CognoMeetRecordings'


class CognoMeetAuditTrail(models.Model):
    cogno_meet_io = models.ForeignKey(
        'CognoMeetIO', null=True, blank=False, on_delete=models.CASCADE)

    cogno_meet_recording = models.ManyToManyField(
        'CognoMeetRecording', blank=True)

    meeting_screenshorts_urls = models.TextField(
        default="{\"items\":[]}", help_text="Meeting Screenshot", null=True, blank=True)

    meeting_feedback_customer = models.TextField(null=True, blank=True)

    meeting_feedback_agent = models.TextField(null=True, blank=True)

    agent_rating = models.IntegerField(
        null=True, blank=True, help_text='NPS rating given by client to agent')

    agent_notes = models.TextField(null=True, blank=True)

    customer_location_details = models.TextField(
        default="{\"items\":[]}", help_text="Customer location details", null=True, blank=True)

    total_call_duration = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, help_text='Total meeting  duration (sec)')

    agent_joined_time = models.DateTimeField(
        default=None, null=True, blank=True)

    def __str__(self):
        return str(self.cogno_meet_io.session_id) + ' - CognoMeetAuditTrail'

    def get_support_agents_invited(self):
        try:
            agent_invited_str = ""
            invited_agent_details_obj = CognoMeetInvitedAgentsDetails.objects.filter(
                cogno_meet_io=self.cogno_meet_io).first()
            if invited_agent_details_obj:
                for agent in invited_agent_details_obj.support_agents_invited.all():
                    agent_invited_str += agent_invited_str + agent.user.username + ", "

                if len(agent_invited_str):
                    agent_invited_str = agent_invited_str[:-2]
                    return agent_invited_str

            return "-"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_support_agents_invited %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return "-"

    def get_support_agents_joined(self):
        try:
            agents_joined_str = ""
            invited_agent_details_obj = CognoMeetInvitedAgentsDetails.objects.filter(
                cogno_meet_io=self.cogno_meet_io).first()
            if invited_agent_details_obj:
                for agent in invited_agent_details_obj.support_agents_joined.all():
                    agents_joined_str += agents_joined_str + agent.user.username + ", "

                if len(agents_joined_str):
                    agents_joined_str = agents_joined_str[:-2]
                    return agents_joined_str

            return "-"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_support_agents_joined %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return "-"

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
            meeting_duration = int(self.total_call_duration)
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

    def get_meeting_main_primary_agent(self):
        try:
            main_primary_agent = None
            cogno_meet_conf_obj = self.cogno_meet_io
            if cogno_meet_conf_obj:
                session_id = cogno_meet_conf_obj.session_id
                cobrowse_io = CognoMeetIO.objects.filter(
                    session_id=session_id).first()
                if cobrowse_io:
                    main_primary_agent = cobrowse_io.cogno_meet_agent.user.username

            return main_primary_agent
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_meeting_main_primary_agent %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def get_meeting_screenshot(self):
        try:
            meeting_screenshot = json.loads(self.meeting_screenshorts_urls)
            return meeting_screenshot['items']
        except Exception:
            return []

    def actual_meeting_start_time(self):
        try:
            actual_start_end_time = MeetingActualStartEndTime.objects.filter(
                cogno_meet_io=self.cogno_meet_io).first()
            if actual_start_end_time:
                return actual_start_end_time.start_time, actual_start_end_time.end_time
        except Exception:
            return None

    class Meta:
        verbose_name = 'CognoMeetAuditTrail'
        verbose_name_plural = 'CognoMeetAuditTrail'


class CognoMeetChatHistory(models.Model):
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    cogno_meet_io = models.ForeignKey(
        'CognoMeetIO', null=True, blank=False, on_delete=models.CASCADE)

    message = models.TextField(null=True, blank=True)

    attachment_file_name = models.TextField(
        null=True, blank=True, max_length=2000)

    attachment_file_path = models.TextField(
        null=True, blank=True, max_length=2000)

    datetime = models.DateTimeField(
        null=True, blank=True, default=timezone.now)

    sender = models.CharField(
        max_length=256, null=False, blank=False, choices=CHAT_SENDER)

    sender_name = models.ForeignKey(
        'CognoMeetAgent', null=True, blank=True, on_delete=models.CASCADE)

    sender_id = models.TextField(
        null=True, blank=True, default="", help_text="This field will consist of the participant ID which we have received from Dyte")

    external_participant_name = models.TextField(
        null=True, blank=True, default="", help_text="In a meeting when external participants are invited (via mail), the name of them are stored here along with customer's name.")

    def mask_customer_chat(self):
        try:
            if self.message != "" and self.cogno_meet_io.cogno_meet_access_token and self.cogno_meet_io.cogno_meet_access_token.enable_PII_masking == True:
                self.message = hash_crucial_info_in_data(self.message)
                self.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error on saving CognoMeetChatHistory %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeetApp'})

    def __str__(self):
        return str(self.cogno_meet_io.session_id) + ' - ' + str(self.attachment_file_name if self.message == None else self.message)

    class Meta:
        verbose_name = 'CognoMeetChatHistory'
        verbose_name_plural = 'CognoMeetChatHistory'


class CognoMeetFileAccessManagement(models.Model):
    key = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text=UNIQUE_ACCESS_TOKEN_KEY)

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    is_public = models.BooleanField(default=True)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True, help_text="Original name of file without adding any marker to make it unique")

    cogno_meet_access_token = models.ForeignKey(
        'CognoMeetAccessToken', default=None, null=True, blank=True, on_delete=models.CASCADE, help_text=COGNOMEET_ACCESS_TOKEN)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime when access management object is created')

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.is_public)

    class Meta:
        verbose_name = 'CognoMeetFileAccessManagement'
        verbose_name_plural = 'CognoMeetFileAccessManagement'

    def is_obj_time_limit_exceeded(self):
        try:
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
                           str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return True


class AuthTokenDetail(models.Model):
    cogno_meet_io = models.ForeignKey(
        'CognoMeetIO', null=True, blank=False, on_delete=models.CASCADE)

    request_payload = models.TextField(null=True, blank=True)

    response_payload = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.cogno_meet_io.session_id) + "- AuthTokenDetail"

    class Meta:
        verbose_name = 'AuthTokenDetail'
        verbose_name_plural = 'AuthTokenDetails'


class CognoMeetInvitedAgentsDetails(models.Model):

    cogno_meet_io = models.ForeignKey(
        CognoMeetIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    support_agents_invited = models.ManyToManyField(
        CognoMeetAgent, blank=True, related_name="support_agents_invited", help_text="Stores the list of support agents that have been invited for the particular cognomeet session")

    support_agents_joined = models.ManyToManyField(
        CognoMeetAgent, blank=True, related_name="support_agents_joined", help_text="Stores the list of support agents that have joined the particular cognomeet session")

    def __str__(self):
        str_value = "Session ID - " + str(self.cogno_meet_io.session_id)
        return str_value

    class Meta:
        verbose_name = 'CognoMeetInvitedAgentsDetails'
        verbose_name_plural = 'CognoMeetInvitedAgentsDetails'


class CognoMeetCronjobTracker(models.Model):

    cronjob_id = models.CharField(max_length=100, null=True, blank=True,
                                  help_text='a unique ID of the cronjob being executed')

    creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the cronjob tracker object was created')

    def __str__(self):
        try:
            return str(self.cronjob_id)
        except Exception:
            return "-"

    class Meta:
        verbose_name = 'CognoMeetCronjobTracker'
        verbose_name_plural = 'CognoMeetCronjobTracker'


class MeetingActualStartEndTime(models.Model):
    start_time = models.DateTimeField(
        null=True, blank=True, help_text='Schedule meet actual start time')

    end_time = models.DateTimeField(
        null=True, blank=True, help_text='Schedule meet actual end time')

    cogno_meet_io = models.ForeignKey(
        CognoMeetIO, on_delete=models.CASCADE, default=None, null=True, blank=True, help_text='Cobrowsing session object')

    class Meta:
        verbose_name = 'MeetingActualStartEndTime'
        verbose_name_plural = 'MeetingActualStartEndTime'


class CognoMeetExportDataRequest(models.Model):

    agent = models.ForeignKey(
        'CognoMeetAgent', null=True, blank=True, on_delete=models.CASCADE, help_text="Stores the agent object of who has raised the request")

    report_type = models.CharField(
        max_length=256, null=False, blank=False, choices=REPORT_TYPE_CHOICES, help_text="Stores the type of report requested")

    export_request_datetime = models.DateTimeField(
        default=timezone.now, help_text="The time at when the request was registered")

    filter_param = models.TextField(
        null=True, blank=True, help_text="The details of the required export (for ex: date range)")

    is_completed = models.BooleanField(
        default=False, help_text="If the export is successfully completed then we set it as true.")

    def __str__(self):
        return str(self.agent.user.username)

    class Meta:
        verbose_name = 'CognoMeetExportDataRequest'
        verbose_name_plural = 'CognoMeetExportDataRequest'
