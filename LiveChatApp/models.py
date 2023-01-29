# -*- coding: utf-8 -*-
from __future__ import unicode_literals

############     Django App  ###################

import uuid
from django import template
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_delete

################# Application #################

import sys
import json
import logging
from EasyChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils import get_admin_from_active_agent, get_admin_config, get_customer_blacklisted_keywords, is_agent_live, send_event_for_login_logout, send_event_for_performance_report, handle_agent_not_ready
from LiveChatApp.utils_email import get_email_config_obj
############     Logger  ###################

logger = logging.getLogger(__name__)


class LiveChatCategory(models.Model):

    title = models.CharField(max_length=100, help_text="Name of issue")

    priority = models.CharField(
        max_length=1, default=1, null=False, blank=False, choices=PRIORITY_VALUES)
    bot = models.ForeignKey(Bot, null=True,
                            blank=True, on_delete=models.CASCADE, help_text="Specific bots for category")

    is_public = models.BooleanField(
        default=True, null=False, blank=False, help_text="Category type is public or not")

    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether Category is deleted or not. Select this instead of deleting the user.")

    class Meta:
        verbose_name = "LiveChatCategory"
        verbose_name_plural = "LiveChatCategories"

    def __str__(self):
        try:
            return str(self.title) + " " + str(self.bot.name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in LiveChatCategory %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
            return "No Name"

    def get_category_name(self):
        try:
            return str(self.title) + " - " + str(self.bot.name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in get_category_name %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
            return "No Name"        


class LiveChatUser(models.Model):

    status = models.CharField(max_length=1,
                              default="3",
                              null=False,
                              blank=False,
                              choices=ROLES)

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True)

    livechat_level = models.CharField(max_length=10,
                                      default="1",
                                      null=False,
                                      blank=False,
                                      choices=LIVECHAT_LEVEL)

    agents = models.ManyToManyField(
        'LiveChatUser', blank=True, related_name="agent", help_text='LiveChat Agent/Manager under admin or Agent under Manager')

    bots = models.ManyToManyField(
        Bot, blank=True, help_text="Specific bots shared with this agent.")

    category = models.ManyToManyField(
        'LiveChatCategory', blank=True, help_text="Designates, this agent can resolve the issues related to this category.")

    phone_number = models.CharField(
        max_length=50, null=True, blank=True, help_text="Phone number of live chat user")

    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether user is deleted or not. Select this instead of deleting the user.")

    profile_pic = models.FileField(
        upload_to="profile/", default="profile/default.png", null=True, blank=True, help_text="Profile picture of live chat user.")

    is_online = models.BooleanField(
        default=False, help_text=USER_ONLINE_OFFLINE)

    logging_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user logged in")

    last_updated_time = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Last updated date and time.")

    resolved_chats = models.IntegerField(
        default=0, help_text="This much of chats are resolved by the LiveChatUser in the current session.")

    is_allow_toggle = models.BooleanField(
        default=False, help_text="If this toggle is set to True, then the user would be able to toggle between the role of Admin and Agent.")

    notification = models.BooleanField(
        default=False, help_text="Designates whether user has enabled desktop notification or not.")

    current_status = models.CharField(
        max_length=2, default="7", null=False, blank=False, choices=LIVECHAT_AUDIT_TRAIL_ACTIONS)

    status_changed_by_admin_supervisor = models.BooleanField(
        default=False, help_text="Designates whether admin/supervisor has marked this agent as offline or not.")

    is_session_exp = models.BooleanField(
        default=True, help_text="Designates whether user is loggedIn or not.")

    static_analytics = models.BooleanField(
        default=False, help_text='show static analytics for demo')

    meeting_host_url = models.CharField(
        max_length=2048, default='meet.allincall.in')

    last_chat_assigned_time = models.DateTimeField(
        default=timezone.now, help_text="Last updated date and time.")

    is_livechat_only_admin = models.BooleanField(
        default=False, help_text='If user is only LiveChat admin(no easychat access')

    livechat_only_admin = models.ManyToManyField(
        'LiveChatUser', blank=True, related_name="only_admin", help_text='LiveChat only admin under current admin')

    ongoing_chats = models.IntegerField(
        default=0, help_text="This denotes the number of ongoing chats in the current session.")

    max_customers_allowed = models.IntegerField(
        default=-1, help_text="Maximum number of customer can assigned to the agent.")

    preferred_languages = models.ManyToManyField(
        'EasyChatApp.Language', blank=True, help_text="Preferred languages by agent.")

    last_followup_lead_assigned_time = models.DateTimeField(
        default=timezone.now, help_text="Last time when a follow up lead was assigned to this agent.")

    enable_chat_escalation_for_supervisor = models.BooleanField(
        default=False, help_text="Designates whether supervisor can access chat escalation functionalities.")

    last_email_chat_assigned_time = models.DateTimeField(
        default=timezone.now, help_text="Last time when a email chat was assigned to this agent.")

    ameyo_agent_id = models.CharField(max_length=2048, null=True, blank=True, default="", help_text="Ameyo agent ID.")

    ameyo_agent_name = models.CharField(max_length=100, null=True, blank=True, default="", help_text="Name of the ameyo agent.")

    def __str__(self):
        return str(self.user.username)

    def name(self):
        return self.username

    def mark_online(self):
        try:
            self.logging_time = timezone.now()
            self.is_session_exp = False
            incomplete_session = LiveChatSessionManagement.objects.filter(
                session_completed=False, user=self)
            handle_agent_not_ready(self.user.username, LiveChatUser, LiveChatSessionManagement, LiveChatConfig, LiveChatAdminConfig, Bot)
            if incomplete_session.count():
                incomplete_session = incomplete_session[0]
                if incomplete_session.user.is_online:
                    diff = timezone.now() - \
                        incomplete_session.session_ends_at
                    incomplete_session.online_time += diff.seconds
                    diff = timezone.now() - incomplete_session.user.last_updated_time
                    incomplete_session.offline_time += diff.seconds
                    incomplete_session.session_ends_at = timezone.now()
                    incomplete_session.session_completed = True
                    incomplete_session.save()
                else:
                    diff = timezone.now() - incomplete_session.session_ends_at
                    incomplete_session.offline_time += diff.seconds
                    incomplete_session.session_ends_at = timezone.now()
                    incomplete_session.session_completed = True
                    incomplete_session.save()
                send_event_for_login_logout(self, incomplete_session, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot, True)
                send_event_for_performance_report(self, incomplete_session, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot, True)
            livechat_session_management = LiveChatSessionManagement.objects.create(user=self)
            send_event_for_login_logout(self, livechat_session_management, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
            send_event_for_performance_report(self, livechat_session_management, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
            self.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat mark online %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

    def get_public_category(self):
        category = ""
        try:
            for item in self.bots.filter(is_deleted=False):
                for item in self.category.filter(bot=item, is_public=True, is_deleted=False):
                    category += str(item.title) + ", "
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get category %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        return category[:-2]

    def get_bot_list(self):
        bot_list = ""
        try:
            admin = get_admin_from_active_agent(self, LiveChatUser)
            bot_objs = admin.bots.filter(is_deleted=False)

            for item in self.bots.filter(is_deleted=False):
                if item in bot_objs:
                    bot_list += str(item.name) + ", "

            if bot_list == '':
                return '-'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get bot list %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return bot_list[:-2]

    def get_current_status(self):
        current_status = ""
        try:
            current_status = LIVECHAT_AUDIT_TRAIL_ACTION_DICT[
                self.current_status]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get current status %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return current_status

    def get_supervisor(self):
        try:
            parent_users = LiveChatUser.objects.filter(
                agents__user=self.user).values("user__username")
            final_string = ""
            for parent_user in parent_users:
                final_string = parent_user["user__username"] + \
                    ", " + final_string
            if final_string != "":
                return final_string[:-2]
            return "Self"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get supervisor %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
            return "Self"

    def get_supervisor_pk(self):
        try:
            parent_user = LiveChatUser.objects.filter(
                agents__user=self.user)[0]
            return parent_user.pk
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get supervisor pk %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
            return "-1"

    def check_livechat_status(self):
        try:
            import pytz
            import os
            import datetime
            tz = pytz.timezone(settings.TIME_ZONE)
            if os.path.exists(settings.MEDIA_ROOT + 'agents/' + str(self.user.username) + ".txt"):
                file_agent = open(settings.MEDIA_ROOT + "agents/" +
                                  str(self.user.username) + ".txt", "r")
                last_updated_time_from_file = file_agent.readline()
                date_format = "%m/%d/%Y, %H:%M:%S"
                last_updated_time_from_file = datetime.datetime.strptime(
                    last_updated_time_from_file, date_format)
                last_updated_time = last_updated_time_from_file.astimezone(tz)
                file_agent.close()
            else:
                last_updated_time = self.last_updated_time
                if last_updated_time == None:
                    return False
            last_updated_time = last_updated_time.astimezone(tz)
            current_time = timezone.now().astimezone(tz)
            available_time = (current_time - last_updated_time).total_seconds()

            if available_time > 75:
                return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in check_livechat_status %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        return True

    def get_max_customer_count(self):
        try:
            if self.max_customers_allowed == -1:
                livechat_config = LiveChatConfig.objects.get(
                    bot=self.bots.all()[0])
                return livechat_config.max_customer_count

            else:
                return self.max_customers_allowed

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in getting max customer count%s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

    def get_agent_name(self):
        try:
            if str(self.user.first_name).strip() == "":
                agent_fullname = str(
                    self.user.username).strip()
            else:
                agent_fullname = str(self.user.first_name).strip(
                ) + " " + str(self.user.last_name).strip()

            return agent_fullname
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in getting agent name %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return ""

    def is_voip_enabled(self):
        try:
            bots = self.bots.filter(is_deleted=False)

            for bot in bots:
                config_obj = LiveChatConfig.objects.get(bot=bot)

                if config_obj.is_voip_enabled:
                    return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_voip_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return False

    def is_raise_ticket_enabled(self):
        try:
            bots = self.bots.filter(is_deleted=False)

            for bot in bots:
                config_obj = LiveChatConfig.objects.get(bot=bot)

                if config_obj.is_agent_raise_ticket_functionality_enabled:
                    return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_raise_ticket_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return False

    def is_followup_lead_enabled(self):
        try:
            bots = self.bots.filter(is_deleted=False)

            for bot in bots:
                config_obj = LiveChatConfig.objects.get(bot=bot)

                if config_obj.is_followup_lead_enabled:
                    return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_followup_lead_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return False

    def is_vc_enabled(self):
        try:
            bots = self.bots.filter(is_deleted=False)

            for bot in bots:
                config_obj = LiveChatConfig.objects.get(bot=bot)

                if config_obj.is_livechat_vc_enabled:
                    return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_vc_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return False

    def is_cobrowsing_enabled(self):
        try:
            bots = self.bots.filter(is_deleted=False)

            for bot in bots:
                config_obj = LiveChatConfig.objects.get(bot=bot)

                if config_obj.is_cobrowsing_enabled:
                    return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_voip_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return False

    def is_chat_escalation_enabled(self):
        try:
            admin_config = get_admin_config(self, LiveChatAdminConfig, LiveChatUser)

            if self.status == "1":
                return admin_config.is_chat_escalation_matrix_enabled
            elif self.status == "2":
                return admin_config.is_chat_escalation_matrix_enabled and self.enable_chat_escalation_for_supervisor

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_chat_escalation_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return False

    def is_email_analytics_enabled(self):
        try:
            admin_config = get_admin_config(self, LiveChatAdminConfig, LiveChatUser)

            email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

            if email_config_obj.is_livechat_enabled_for_email and email_config_obj.is_successful_authentication_complete:
                return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_email_analytics_enabled %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return False
    
    def get_agents_assigned_count(self):
        try:
            return self.agents.filter(is_deleted=False).count()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in get_agents_assigned_count %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return 0
    
    def get_active_agents_count(self):
        try:
            agents = self.agents.filter(is_deleted=False)

            count = 0
            for agent in agents:
                if agent.is_online and is_agent_live(agent):
                    count += 1
            
            return count
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in get_active_agents_count %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return 0

    def get_ongoing_chats_count(self):
        try:
            ongoing_chats = self.agents.filter(is_deleted=False).aggregate(Sum('ongoing_chats'))['ongoing_chats__sum']

            if ongoing_chats == None:
                ongoing_chats = 0

            return ongoing_chats
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in get_ongoing_chats_count %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return 0

    def check_supervisor_bot(self, supervisor):
        try:
            bot_obj = self.bots.filter(is_deleted=False).first()

            if bot_obj in supervisor.bots.filter(is_deleted=False):
                return True
            
            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in check_supervisor_bot %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        
        return False

    class Meta:
        verbose_name = "LiveChatUser"
        verbose_name_plural = "LiveChatUser"


class LiveChatAuditTrail(models.Model):

    user = models.ForeignKey('LiveChatUser', null=True,
                             blank=True, on_delete=models.CASCADE)

    action = models.CharField(max_length=2, null=False,
                              choices=LIVECHAT_AUDIT_TRAIL_ACTIONS, help_text="Action by user.")

    datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time of action.")

    data = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        return self.user.user.username + " - " + self.action

    class Meta:
        verbose_name = 'LiveChatAuditTrail'
        verbose_name_plural = 'LiveChatAuditTrails'
        ordering = ['-pk']


class LiveChatBlackListKeyword(models.Model):
    word = models.CharField(
        max_length=100, help_text="Word, which needs to be blacklisted.")
    agent_id = models.ForeignKey('LiveChatUser', null=True, blank=True,
                                 on_delete=models.CASCADE, help_text="Agent")
    blacklist_keyword_for = models.CharField(max_length=256, default="agent", null=False, blank=False, choices=BLACKLIST_KEYWORD_FOR)

    class Meta:
        verbose_name = "LiveChatBlackListKeyword"
        verbose_name_plural = "LiveChatBlackListKeywords"

    def __str__(self):
        return self.word


class LiveChatCalender(models.Model):

    event_type = models.CharField(max_length=1,
                                  default="1",
                                  null=False,
                                  blank=False,
                                  choices=LIVECHAT_EVENT_TYPE)
    event_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time of the event.")
    description = models.CharField(max_length=100, default="")
    auto_response = models.TextField(
        null=True, blank=True, help_text="this text will be shown to customer in case of holiday.")
    created_by = models.ForeignKey('LiveChatUser', null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="creator", help_text="LiveChatUser(Admin/Manager)")
    applicable_for = models.ManyToManyField(
        'LiveChatUser', blank=True, help_text="Calender applicable to selected users.")
    modified_by = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="modifier", help_text="LiveChatUser(Admin/Manager)")
    created_at = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user created this event.")
    modified_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time, when this event got modified.")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "LiveChatCalender"
        verbose_name_plural = "LiveChatCalenders"

    def __str__(self):
        return self.description


class LiveChatConfig(models.Model):

    max_customer_count = models.IntegerField(
        default=1, help_text="Maximum number of customer can assigned to the agent.")
    category_enabled = models.BooleanField(
        default=False, help_text="Designates whether category feature enabled or not.")
    auto_bot_response = models.TextField(
        default="Thanks for contacting us. All our agents are currently offline. Please try again during working hours.", blank=True, help_text="Bot response for a none working hour request.")
    queue_timer = models.IntegerField(
        default=30, help_text="Waiting time for customer to be assigned to agent in seconds")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, null=True, blank=True,
                            help_text='Livechat user bot')
    agent_unavialable_response = models.CharField(
        max_length=2048, null=True, blank=True, default="Our chat representatives are unavailable right now. Please try again in some time.")

    masking_enabled = models.BooleanField(
        default=True, help_text="Designates whether masking pii data is enabled or not")

    auto_chat_disposal_enabled = models.BooleanField(
        default=True, help_text="Designates whether auto chat disposal is enabled or not.")

    user_terminates_chat_enabled = models.BooleanField(
        default=True, help_text="Designates whether auto chat disposal when user terminates chat is enabled or not.")

    user_terminates_chat_dispose_time = models.IntegerField(
        default=2, help_text="Time after which chat should dispose when user terminates chat (in min).")

    session_inactivity_enabled = models.BooleanField(
        default=True, help_text="Designates whether auto chat disposal on session inactivity is enabled or not.")

    session_inactivity_chat_dispose_time = models.IntegerField(
        default=5, help_text="Time after which chat should dispose on session inactivity (in min).")

    system_commands = models.TextField(
        null=True, default="['os.system', 'subprocess', 'import threading', 'threading.Thread', 'ssh']")

    access_token = models.UUIDField(default=uuid.uuid4,
                                    editable=False, help_text='unique access_token')

    max_guest_agent = models.CharField(
        max_length=1, default="1", null=False, blank=False, choices=LIVECHAT_GUEST_AGENT)

    guest_agent_timer = models.IntegerField(
        default=60, help_text="Pending time for accept/reject while an agent invites another agent in the chat(In seconds)")

    is_voip_enabled = models.BooleanField(
        default=False, help_text="Designates whether voip during livechat is enabled or not")

    call_type = models.CharField(
        max_length=256, null=True, blank=True, choices=CALL_TYPE, help_text="Designates whether call type is PIP, New Tab or Video Call")

    is_call_from_customer_end_enabled = models.BooleanField(
        default=True, help_text="Designates whether customers can initiate call or not")

    is_livechat_vc_enabled = models.BooleanField(
        default=False, help_text="Designates whether livechat supports video call or not")

    is_virtual_interpretation_enabled = models.BooleanField(
        default=True, help_text="Designates whether admin has enabled virtual interpretation option for agents")

    is_original_information_in_reports_enabled = models.BooleanField(
        default=True, help_text="Designates whether displaying of original information of a customer is enabled in reports.")
        
    meeting_domain = models.TextField(
        null=True, default="meet-uat.allincall.in", help_text="Domain for LiveChat voice/video meeting")

    is_agent_raise_ticket_functionality_enabled = models.BooleanField(
        default=False, help_text="Designates whether livechat agent can raise a ticket")

    is_customer_details_editing_enabled = models.BooleanField(
        default=True, help_text="Designates whether admin has enabled editing customer details for agents")

    is_transcript_enabled = models.BooleanField(
        default=False, help_text="Designates whether admin has enabled email transcript functionality or not")
    
    is_cobrowsing_enabled = models.BooleanField(
        default=False, help_text="Designates whether Cobrowsing is enabled in LiveChat or not")

    cobrowse_request_text = models.TextField(
        default=COBROWSING_REQUEST_TEXT, help_text="Text to be displayed to customer when agent requests for cobrowsing")
    
    is_followup_lead_enabled = models.BooleanField(
        default=False, help_text="Designates whether the agents has to be assigned to follow up leads.")

    followup_lead_sources = models.TextField(
        default='["offline_chats", "missed_chats", "abandoned_chats"]', null=True, blank=True, help_text="Sources of follow up leads.")

    is_whatsapp_reinitiation_enabled = models.BooleanField(
        default=False, help_text="Designates whether the agents can reinitiate conversation for whatsapp followup leads.")

    whatsapp_reinitiating_text = models.TextField(
        default="Hi! It looks like we missed you when you tried to communicate. Our agents are now available. Reply with a &#039;Yes&#039; if you want to continue the interactions.", 
        help_text="Text to be displayed to customer when agent reinitiates conversation for whatsapp channel.")

    whatsapp_reinitiating_keyword = models.TextField(
        default="Yes", help_text="Keyword that will trigger the livechat intent from whatsapp channel.")

    class Meta:
        verbose_name = "LiveChatConfig"
        verbose_name_plural = "LiveChatConfigs"

    def __str__(self):
        if self.bot:
            return str(self.bot.name) + "-" + str(self.max_customer_count)
        return "No Bot - " + str(self.pk)

    def save(self, *args, **kwargs):
        super(LiveChatConfig, self).save(*args, **kwargs)


class CannedResponse(models.Model):

    status = models.CharField(max_length=10, null=True,
                              blank=True, choices=CANNED_RESPONSE_STATUS)
    agent_id = models.ForeignKey('LiveChatUser', null=True, blank=True,
                                 on_delete=models.CASCADE, help_text="Agent")
    title = models.CharField(max_length=100, null=True, blank=True,
                             default="", help_text="Title of canned response")
    keyword = models.CharField(
        max_length=100, null=True, blank=True, default="", help_text="Keyword for canned response.")
    response = models.TextField(
        default="", null=True, blank=True, help_text="Response of given canned title.")
    is_deleted = models.BooleanField(
        default=False, help_text="Designates whether canned response is deleted or not. Select this instead of deleting this canned response.")

    def name(self):
        return self.keyword

    class Meta:
        verbose_name = "CannedResponse"
        verbose_name_plural = "CannedResponses"

    def save(self, *args, **kwargs):
        super(CannedResponse, self).save(*args, **kwargs)


class LiveChatTransferAudit(models.Model):

    livechat_customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                          on_delete=models.CASCADE, db_index=True)
    chat_transferred_by = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.CASCADE,
                                            related_name="chat_transferred_by", help_text="Agent id who has transferred the chat of this customer")

    chat_transferred_to = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.CASCADE,
                                            related_name="chat_transferred_to", help_text="Agent id who has transferred the chat of this customer")

    transfer_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when of chat was transferred.")

    transfer_description = models.TextField(
        default="", null=True, blank=True, help_text="Reason for transferring chat")

    def __str__(self):
        return str(self.livechat_customer.session_id)

    class Meta:
        verbose_name = "LiveChatTransferAudit"
        verbose_name_plural = "LiveChatTransferAudit"


class LiveChatMISDashboard(models.Model):

    message_id = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text='Unique message ID')

    livechat_customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                          on_delete=models.CASCADE, db_index=True)

    sender = models.CharField(max_length=100,
                              default="Customer",
                              null=False,
                              blank=False,
                              choices=LIVECHAT_SENDER)

    sender_name = models.CharField(max_length=100,
                                   default="Customer",
                                   null=False, blank=False,
                                   help_text="Name of sender")
    text_message = models.TextField(
        default="", null=True, blank=True, help_text="Message received or sent")
    attachment_file_name = models.TextField(
        default="", null=True, blank=True, help_text="Attachment File Name")
    attachment_file_path = models.TextField(
        default="", null=True, blank=True, help_text="Path of attachment file")
    preview_attachment_file_path = models.TextField(
        default="", null=True, blank=True, help_text="Path for preview attachment of  file")
    message_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when of message")
    thumbnail_file_path = models.TextField(
        default="", null=True, blank=True, help_text="Path of attachment file's thumbnail")
    is_guest_agent_message = models.BooleanField(
        default=False, help_text="If the message was sent by guest agent.")
    sender_username = models.CharField(
        max_length=100, default="", null=True, blank=True, help_text="Agent's username")
    reply_message_id = models.TextField(
        default="", null=True, blank=True, help_text="ID of the message for which supervisor/admin has given a reply")
    translated_text = models.TextField(
        default="", null=True, blank=True, help_text="Translated text is to store message as per customer's preferred language")
    meeting_link = models.TextField(
        default="", null=True, blank=True, help_text="Meeting link generated for video call")
    is_voice_call_message = models.BooleanField(
        default=False, help_text="If the message was voice call notification.")
    is_video_call_message = models.BooleanField(
        default=False, help_text="If the message was video call notification.")
    is_cobrowsing_message = models.BooleanField(
        default=False, help_text="If the message was cobrowsing notification.")
    is_transcript_message = models.BooleanField(
        default=False, help_text="If the message was transcript notification.")
    message_for = models.CharField(max_length=100,
                                    null=True,
                                    blank=True,
                                    choices=VIDEO_CALL_MESSAGE_FOR,
                                    help_text="To whom this message belongs, if message is video call notification.")   
    is_customer_warning_message = models.BooleanField(
        default=False, help_text="If the message was customer warning message.")
    is_customer_report_message_notification = models.BooleanField(
        default=False, help_text="If the message was customer report message notification.")
    message_contains_blacklisted_keyword = models.BooleanField(
        default=False, help_text="If the message contains blacklisted keyword/s.")
    is_copied_from_easychat = models.BooleanField(
        default=False, help_text="Designates whether this message was copied from easychat MISDashboard")
    is_file_not_support_message = models.BooleanField(
        default=False, help_text="If the message was file not support notification.")

    def __str__(self):
        return str(self.livechat_customer.session_id)

    class Meta:
        verbose_name = "LiveChatMISDashboard"
        verbose_name_plural = "LiveChatMISDashboard"


@receiver(post_save, sender=LiveChatMISDashboard)
def check_message_for_blacklisted(sender, instance, **kwargs):
    try:
        if instance.sender == "Customer" and instance.livechat_customer:

            if instance.livechat_customer.agent_id:
                admin_config = get_admin_config(instance.livechat_customer.agent_id, LiveChatAdminConfig, LiveChatUser)

                if admin_config.is_chat_escalation_matrix_enabled:
                    customer_blacklisted_keywords = get_customer_blacklisted_keywords(instance.livechat_customer.agent_id, LiveChatBlackListKeyword, LiveChatUser)
                    customer_blacklisted_keywords = list(customer_blacklisted_keywords.values_list('word', flat=True))
                    customer_blacklisted_keywords = customer_blacklisted_keywords + DEFAULT_CUSTOMER_BLACKLISTED_KEYWORDS

                    message = instance.text_message.lower()
                    for customer_blacklisted_keyword in customer_blacklisted_keywords:
                        if message.find(customer_blacklisted_keyword.lower()) != -1:
                            LiveChatMISDashboard.objects.filter(pk=instance.pk).update(message_contains_blacklisted_keyword=True)
                            break

    except Exception:
        pass 


class LiveChatCustomer(models.Model):

    # Session detail
    session_id = models.UUIDField(default=uuid.uuid4, primary_key=True,
                                  editable=False, db_index=True, help_text=UNIQUE_SESSION_ID)

    request_raised_date = models.DateField(
        default=now, db_index=True, help_text="Date of session start")
    is_session_exp = models.BooleanField(
        default=False, help_text="Designated whther agent end the chat with user or not.")

    is_denied = models.BooleanField(
        default=False, help_text="Designates whether LiveChat system denied the request or not.")

    abruptly_closed = models.BooleanField(
        default=False, help_text="Designates whether session ended abruptly or not.")
    last_appearance_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time of user last message")
    is_online = models.BooleanField(
        default=False, help_text=USER_ONLINE_OFFLINE)
    joined_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user joined the chat")
    category = models.ForeignKey(LiveChatCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                 help_text="Detones the category of customer based on category of issue.")
    rate_value = models.IntegerField(
        default=-1, help_text="This much rating is given to the agent by the customer at the end of the session.")

    wait_time = models.IntegerField(
        default=0, help_text="Waiting time of customer.")
    chat_duration = models.IntegerField(
        default=0, help_text="Chat duration between customer and agent.")
    group_chat_duration = models.IntegerField(
        default=0, help_text="Group chat duration between customer and agents.")

    unread_message_count = models.IntegerField(
        default=0, help_text="The number of messages which haven't been read.")
    is_system_denied = models.BooleanField(
        default=False, help_text="Designates whether session ended by system(non-working + holidays).")

    queue_time = models.IntegerField(
        default=0, help_text="Waiting time in queue.")
    
    is_chat_loaded = models.BooleanField(
        default=False, help_text="Designates whether session chat loaded at least one time or not.")

    # Customer detail
    client_id = models.CharField(
        max_length=100, default="", null=True, blank=True, db_index=True, help_text="Client ID of the customer provided by client.")
    username = models.CharField(
        max_length=100, default="", null=True, blank=True, help_text="Username of the customer.")

    email = models.CharField(max_length=100, default="", null=True,
                             blank=True, help_text="Email of the customer.")
    phone = models.CharField(default="", max_length=100, null=True,
                             blank=True, help_text="Phone number of the customer.")
    phone_country_code = models.CharField(default="", max_length=10, null=True, blank=True, help_text="Country code of the phone number.")

    customer_language = models.ForeignKey('EasyChatApp.Language', null=True, blank=True, help_text="Language selected by customer while raising request for Livechat.", on_delete=models.SET_NULL)
    
    original_username = models.CharField(
        max_length=100, default="", null=True, blank=True, help_text="Original username of the customer, if it is updated.")
    original_email = models.CharField(
        max_length=100, default="", null=True, blank=True, help_text="Original email of the customer, if it is updated.")
    original_phone = models.CharField(
        default="", max_length=100, null=True, blank=True, help_text="Original phone number of the customer, if it is updated.")

    ip_address = models.TextField(default="", null=True, blank=True)

    is_ameyo_fusion_session = models.BooleanField(
        default=False, help_text="Designates whether following session was requested for cogno livechat or ameyo fusion.")

    # Source of request
    easychat_user_id = models.CharField(max_length=100, default="", null=True,
                                        blank=True, help_text="Easychat_User_id of the customer.")
    bot = models.ForeignKey(Bot, null=True, blank=True, on_delete=models.CASCADE,
                            help_text="Bot id from where user is chatting.")

    channel = models.ForeignKey(
        Channel, null=True, blank=True, on_delete=models.CASCADE, help_text="Bot channel")
    previous_channel = models.TextField(
        default="", null=True, blank=True, help_text="Stores source channel if customer is transferred for email conversation.")
    message = models.TextField(
        default="", null=True, blank=True, help_text="Message given by customer to raise request.")

    system_denied_response = models.TextField(
        default="", null=True, blank=True, help_text="Response that a customer gets in case of denial of livechat request.")
    active_url = models.CharField(max_length=1000, null=True, blank=True,
                                  help_text='active webpage url where client is.')

    source_of_incoming_request = models.CharField(
        max_length=1, choices=LIVECHAT_SOURCE_OF_INCOMING_REQUEST, default='3', 
        help_text="Stores the source details of incoming livechat request.")                              

    # Agent detail
    agent_id = models.ForeignKey('LiveChatUser', related_name="agent_id", null=True, blank=True, db_index=True,
                                 on_delete=models.CASCADE, help_text="Agent")

    agents_group = models.ManyToManyField('LiveChatUser', related_name="agents_group",
                                          blank=True, help_text="Agents who have taken part in this conversation")

    guest_agents = models.ManyToManyField('LiveChatUser', related_name="guest_agents",
                                          blank=True, help_text="Guest agents invited for group chat with customer.")

    guest_session_status = models.TextField(
        default="{}", null=True, blank=True, help_text="Represents the status of the livechat guest agent session")

    chat_ended_by = models.TextField(
        default="", null=True, blank=True, help_text="Customer or Agent ends the chat")

    nps_text_feedback = models.TextField(
        default="", null=True, blank=True, help_text="Nps feedback livechat")

    closing_category = models.ForeignKey(LiveChatCategory, blank=True, null=True, on_delete=models.SET_NULL,
                                         help_text="Detones the category of customer during closing.", related_name="Closing_category")

    is_auto_disposed = models.BooleanField(
        default=False, help_text="Designates whether chat of this customer is auto disposed or not")

    customer_details = models.TextField(
        default="[]", null=True, blank=True, help_text="Details of Customer")

    customer_utility = models.TextField(
        default="[]", null=True, blank=True, help_text="Details of Customer not to be shown on frontend")

    form_filled = models.TextField(
        default="[]", null=True, blank=True, help_text='Form filled by agent when chat is disposed.')

    is_self_assigned_chat = models.BooleanField(
        default=False, help_text="Designates whether chat of this customer is self assigned by the agent")

    is_external = models.BooleanField(
        default=False, help_text="Designates whether chat is raised from external bot or not")

    nps_feedback_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when NPS was given by customer")

    followup_assignment = models.BooleanField(
        default=False, help_text="Designates whether follow up assignment is done for the customer")

    chat_escalation_warn_ignored_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when customer lastly ignored warn notification.")

    is_transcript_request_enabled = models.BooleanField(
        default=False, help_text="Designates whether trancript request is enabled")
    
    transcript_email = models.TextField(
        default="", null=True, blank=True, help_text="Email in which transcript will be send")
    
    is_transcript_sent = models.BooleanField(
        default=False, help_text="Designates whether transcript is sent or not")
    
    agent_first_time_response_time = models.IntegerField(
        default=None, null=True, blank=True, help_text="Time Gap between the agent's first response to end-customer from the time when corresponding LiveChat session gets connected (in seconds)")
    
    class Meta:
        verbose_name = "LiveChatCustomer"
        verbose_name_plural = "LiveChatCustomers"

    def __str__(self):
        return str(self.session_id)

    def name(self):
        return self.username

    def get_messages_list(self):
        try:
            messages_list_obj = LiveChatMISDashboard.objects.filter(
                livechat_customer=self).order_by('message_time', 'pk')
        except Exception:
            messages_list_obj = []
        return messages_list_obj

    def save(self, *args, **kwargs):
        super(LiveChatCustomer, self).save(*args, **kwargs)

    def get_username(self):
        if len(self.username) > 14:
            return self.username[:14] + ".."
        else:
            return self.username

    def get_complete_username(self):
        return self.username

    def get_all_agents(self):
        agent_list = []
        agent_name_list = ""
        try:
            for item in self.mis_dashboard.all():
                if str(item.agent_id.user.username) not in agent_list:
                    agent_list.append(str(item.agent_id.user.username))
                    agent_name_list += str(item.agent_id.user.username) + ", "
        except Exception:
            pass

        return agent_name_list[:-2]

    def get_bot_name(self):
        try:
            return self.bot.name
        except Exception:
            return "None"

    def get_source_name_from_customer_details(self):
        try:
            return json.loads(self.customer_details)[0]["value"]
        except Exception:
            return "Others"
    
    def get_source_name_from_choice_field(self):
        try:
            if self.source_of_incoming_request == '1':
                return "Desktop"
            elif self.source_of_incoming_request == '2':
                return "Mobile"
            elif self.source_of_incoming_request == '3':
                return "Others"
        except Exception:
            return "Others"          
    
    def get_chat_duration(self):
        if self.followup_assignment and not self.agent_id:
            return '-'
        else:
            hour = (self.chat_duration) // 3600
            rem = (self.chat_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            if sec != 0:
                time += str(sec) + "s"
            return time

    def get_wait_time(self):
        hour = (self.queue_time) // 3600
        rem = (self.queue_time) % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "
        if sec != 0:
            time += str(sec) + "s"
        return "0s" if time == "" else time

    def get_if_category_enabled(self):
        livechat_config = LiveChatConfig.objects.filter(bot=self.bot)[0]
        return livechat_config.category_enabled

    def get_system_denied_response(self):
        response = "-"
        try:
            livechat_config = LiveChatConfig.objects.filter(bot=self.bot)[0]
            response = livechat_config.agent_unavialable_response
        except Exception:
            logger.warning("Unable to get system denial response.",
                           extra={"AppName": "LiveChat"})

        return response

    def get_previous_agents(self):
        agent_name_str = "-"
        try:
            user_obj = LiveChatTransferAudit.objects.filter(
                livechat_customer=self).order_by('-pk')[0].chat_transferred_by.user
            prev_agent = user_obj.first_name + " " + \
                user_obj.last_name + " (" + user_obj.username + ")"
            return prev_agent
        except Exception:
            logger.warning("Unable to get previous agents",
                           extra={"AppName": "LiveChat"})

        return agent_name_str

    def get_closing_category_title(self):
        try:
            if self.closing_category:
                return self.closing_category.title
        except Exception:
            logger.warning("Unable to get_closing_category_title",
                           extra={"AppName": "LiveChat"})

        return 'None'

    def get_agent_username(self):
        agent_username = ""
        try:
            if self.followup_assignment and not self.agent_id:
                livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=self)
                agent_username = livechat_followup_cust_obj.agent_id.user.username
            else:
                agent_username = self.agent_id.user.username

        except Exception:
            logger.warning("Unable to get_agent_username",
                           extra={"AppName": "LiveChat"})

        return agent_username

    def get_agent_name(self):
        agent_name = ""
        try:
            if not self.followup_assignment:
                agent_name = self.agent_id.get_agent_name()
            else:
                livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=self)
                agent_name = livechat_followup_cust_obj.agent_id.get_agent_name()

        except Exception:
            logger.warning("Unable to get_agent_name",
                           extra={"AppName": "LiveChat"})

        return agent_name

    def get_last_appearance_date(self):
        import pytz
        tz = pytz.timezone(settings.TIME_ZONE)
        last_appearance_date = self.last_appearance_date.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)
        try:
            if self.followup_assignment and not self.agent_id:
                livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(livechat_customer=self)
                last_appearance_date = livechat_followup_cust_obj.completed_date.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)

        except Exception:
            logger.warning("Unable to get_last_appearance_dat",
                           extra={"AppName": "LiveChat"})

        return last_appearance_date
    
    def get_agent_first_time_response_time(self):
        first_time_response = self.agent_first_time_response_time

        if not first_time_response:
            return 'NR'

        hour = first_time_response // 3600
        rem = first_time_response % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time
    
    def get_cobrowsing_nps_data(self):
        rating_list = 'NA'
        comment_list = 'NA'
        try:
            voip_objects = LiveChatCobrowsingData.objects.filter(customer=self).order_by('start_datetime')

            voip_ratings = list(voip_objects.values_list('rating', flat=True))
            if voip_ratings:
                rating_list = ''
                for rating in voip_ratings:
                    if rating == -1:
                        rating_list += 'NA\n\n'
                    else:
                        rating_list += str(rating) + '\n\n'
                rating_list = rating_list[:-2]

            voip_comments = list(voip_objects.values_list('text_feedback', flat=True))
            if voip_comments:
                comment_list = ''
                for comment in voip_comments:
                    if comment == "":
                        comment_list += 'NA\n\n'
                    else:
                        comment_list += str(comment) + '\n\n'
                comment_list = comment_list[:-2]

        except Exception:
            logger.warning("Unable to get_cobrowsing_nps_data",
                           extra={"AppName": "LiveChat"})

        return rating_list, comment_list


class LiveChatDataExportRequest(models.Model):

    report_type = models.CharField(
        max_length=2, null=True, blank=True, choices=LIVECHAT_REPORT_TYPE)

    request_datetime = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'LiveChatUser', null=False, blank=False, on_delete=models.CASCADE)

    filter_param = models.TextField(default="{}", null=False, blank=False)

    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'LiveChatDataExportRequest'
        verbose_name_plural = 'LiveChatDataExportRequests'

    def __str__(self):
        return self.user.user.username


class LiveChatAgentNotReady(models.Model):

    user = models.ForeignKey('LiveChatUser', null=True,
                             blank=True, on_delete=models.CASCADE)

    session_id = models.UUIDField(default=uuid.uuid4,
                                  editable=False, help_text=UNIQUE_SESSION_ID)

    not_ready_starts_at = models.DateTimeField(default=timezone.now)

    not_ready_ends_at = models.DateTimeField(default=timezone.now)

    reason_for_offline = models.CharField(default="1", max_length=2, null=False,
                                          choices=LIVECHAT_AUDIT_TRAIL_ACTIONS, help_text="Reason for going offline.")
    stop_interaction_duration = models.IntegerField(
        default=0, help_text="Duration for which agent was on stop interaction")
    is_expired = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'LiveChatAgentNotReady'
        verbose_name_plural = 'LiveChatAgentNotReady'

    def __str__(self):
        return str(self.session_id)

    def get_reason_for_offline(self):
        try:
            return LIVECHAT_AUDIT_TRAIL_ACTION_DICT[self.reason_for_offline]
        except Exception:
            return "Adhoc"

    def get_offline_duration(self):
        time = "0s"
        try:
            if self.reason_for_offline != "0" and self.is_expired == False:
                duration = (timezone.now(
                ) - self.not_ready_starts_at).seconds - self.stop_interaction_duration
                self.not_ready_ends_at = timezone.now()
            else:
                duration = (self.not_ready_ends_at -
                            self.not_ready_starts_at).seconds - self.stop_interaction_duration

            hour = (duration) // 3600
            rem = (duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_offline_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return time

    def get_stop_interaction_duration(self):
        time = "0s"
        try:
            duration = self.stop_interaction_duration
            if duration == 0 and self.reason_for_offline == "0":
                duration = (timezone.now() - self.not_ready_starts_at).seconds
                self.not_ready_ends_at = timezone.now()
                self.stop_interaction_duration = duration
            hour = (duration) // 3600
            rem = (duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_stop_interaction_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return time


class LiveChatSessionManagement(models.Model):

    user = models.ForeignKey('LiveChatUser', null=True,
                             blank=True, on_delete=models.CASCADE)

    session_id = models.UUIDField(default=uuid.uuid4,
                                  editable=False, help_text=UNIQUE_SESSION_ID)

    session_starts_at = models.DateTimeField(default=timezone.now)

    session_ends_at = models.DateTimeField(default=timezone.now)

    online_time = models.IntegerField(
        default=0, help_text="Agent logged In and working")

    offline_time = models.IntegerField(
        default=0, help_text="Agent logged In but not working")

    is_idle = models.BooleanField(default=True)

    idle_time = models.IntegerField(
        default=0, help_text="Agent Online but not assigned any chats.")

    last_idle_time = models.DateTimeField(default=timezone.now)

    agent_not_ready = models.ManyToManyField(
        LiveChatAgentNotReady, blank=True, help_text="LiveChatAgentNotReady objects not ready in this session.")

    session_completed = models.BooleanField(default=False)

    time_marked_stop_interaction = models.DateTimeField(
        default=timezone.now, blank=True)

    stop_interaction_time = models.IntegerField(
        default=0, help_text="Time agent was on stop interaction")

    class Meta:
        verbose_name = 'LiveChatSessionManagement'
        verbose_name_plural = 'LiveChatSessionManagements'

    def __str__(self):
        return self.user.user.username

    def get_session_duration(self):
        time = "0s"
        try:
            diff = self.session_ends_at - self.session_starts_at
            session_duration = diff.seconds
            hour = (session_duration) // 3600
            rem = (session_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_session_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return time

    def get_session_stop_interaction_duration(self):
        time = "0s"
        try:
            agent_not_ready_obj = self.agent_not_ready.all()
            if agent_not_ready_obj:
                time = agent_not_ready_obj.aggregate(Sum('stop_interaction_duration'))[
                    "stop_interaction_duration__sum"]
                hour = (time) // 3600
                rem = (time) % 3600
                minute = rem // 60
                sec = rem % 60
                time = ""
                if hour != 0:
                    time = str(hour) + "h "
                if minute != 0:
                    time += str(minute) + "m "
                time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_session_stop_interaction_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return str(time)

    def get_total_offline_time(self):
        time = "0s"
        try:
            agent_not_ready_obj = self.agent_not_ready.all()
            stop_interaction_duration = agent_not_ready_obj.aggregate(
                Sum('stop_interaction_duration'))["stop_interaction_duration__sum"]
            if not stop_interaction_duration:
                stop_interaction_duration = 0
            offline_time = (self.offline_time - stop_interaction_duration)
            hour = (offline_time) // 3600
            rem = (offline_time) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_total_offline_time %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return time

    def get_total_online_time(self):
        time = "0s"
        try:
            hour = (self.online_time) // 3600
            rem = (self.online_time) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_total_online_time %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return time

    def get_name(self):
        return str(self.user.get_agent_name())

    def get_interaction_duration(self):
        interaction_duration = "0s"
        try:

            if self.session_completed:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at)
            else:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at)
            interaction_duration = livechat_customer_objs.aggregate(Sum('chat_duration'))[
                "chat_duration__sum"]

            if interaction_duration == None or interaction_duration == "None":
                return "0s"

            hour = (interaction_duration) // 3600
            rem = (interaction_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            interaction_duration = ""
            if hour != 0:
                interaction_duration = str(hour) + "h "
            if minute != 0:
                interaction_duration += str(minute) + "m "
            interaction_duration += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_interaction_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return interaction_duration

    def get_idle_duration(self):
        idle_duration = "0s"
        try:
            if self.idle_time == 0:
                return "0s"
            hour = (self.idle_time) // 3600
            rem = (self.idle_time) % 3600
            minute = rem // 60
            sec = rem % 60
            idle_duration = ""
            if hour != 0:
                idle_duration = str(hour) + "h "
            if minute != 0:
                idle_duration += str(minute) + "m "
            if sec != 0:
                idle_duration += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in idle_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return idle_duration

    def get_average_handle_time(self):
        average_handle_time = "0s"
        try:

            if self.session_completed:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at)
            else:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at)

            average_handle_time = livechat_customer_objs.aggregate(Sum('chat_duration'))[
                "chat_duration__sum"]

            if average_handle_time == None or average_handle_time == "None":
                return "0s"

            agent_count = livechat_customer_objs.count()

            average_handle_time = average_handle_time // agent_count
            hour = (average_handle_time) // 3600
            rem = (average_handle_time) % 3600
            minute = rem // 60
            sec = rem % 60
            average_handle_time = ""
            if hour != 0:
                average_handle_time = str(hour) + "h "
            if minute != 0:
                average_handle_time += str(minute) + "m "
            average_handle_time += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_average_handle_time %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return average_handle_time

    def get_not_ready_count(self):
        return self.agent_not_ready.all().count()

    def get_interaction_count(self):
        primary_agent_count = LiveChatCustomer.objects.filter(
            agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at).count()
        secondary_agent_count = LiveChatGuestAgentAudit.objects.filter(
            livechat_agent=self.user, action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at, action="accept").count()
        return (primary_agent_count + secondary_agent_count)

    def get_total_transferred_chat_received(self):

        if self.session_completed:
            livechat_transfer_audit_objs = LiveChatTransferAudit.objects.filter(
                chat_transferred_to=self.user, transfer_datetime__gte=self.session_starts_at, transfer_datetime__lte=self.session_ends_at)
        else:
            livechat_transfer_audit_objs = LiveChatTransferAudit.objects.filter(
                chat_transferred_to=self.user, transfer_datetime__gte=self.session_starts_at)

        return livechat_transfer_audit_objs.count()

    def get_total_transferred_chat_made(self):

        if self.session_completed:
            livechat_transfer_audit_objs = LiveChatTransferAudit.objects.filter(
                chat_transferred_by=self.user, transfer_datetime__gte=self.session_starts_at, transfer_datetime__lte=self.session_ends_at)
        else:
            livechat_transfer_audit_objs = LiveChatTransferAudit.objects.filter(
                chat_transferred_by=self.user, transfer_datetime__gte=self.session_starts_at)
        return livechat_transfer_audit_objs.count()

    def get_total_group_chat_request(self):

        if self.session_completed:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="request", action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at)
        else:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="request", action_datetime__gte=self.session_starts_at)

        return livechat_group_chat_objs.count()

    def get_total_group_chat_accept(self):

        if self.session_completed:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="accept", action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at)
        else:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="accept", action_datetime__gte=self.session_starts_at)

        return livechat_group_chat_objs.count()

    def get_total_group_chat_reject(self):

        if self.session_completed:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="reject", action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at)
        else:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="reject", action_datetime__gte=self.session_starts_at)

        return livechat_group_chat_objs.count()

    def get_total_group_chat_no_response(self):

        if self.session_completed:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="no_response", action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at)
        else:
            livechat_group_chat_objs = LiveChatGuestAgentAudit.objects.filter(
                livechat_agent=self.user, action="no_response", action_datetime__gte=self.session_starts_at)

        return livechat_group_chat_objs.count()

    def get_total_group_chat_duration(self):
        group_interaction_duration = "0s"
        try:

            if self.session_completed:
                livechat_guest_agent_audits = LiveChatGuestAgentAudit.objects.filter(
                    livechat_agent=self.user, action_datetime__gte=self.session_starts_at, action_datetime__lte=self.session_ends_at, action="accept").values_list('livechat_customer', flat=True).distinct()
            else:
                livechat_guest_agent_audits = LiveChatGuestAgentAudit.objects.filter(
                    livechat_agent=self.user, action_datetime__gte=self.session_starts_at, action="accept").values_list('livechat_customer', flat=True).distinct()

            guest_agent_group_chat_duration = 0
            for livechat_guest_agent_audit in livechat_guest_agent_audits:
                livechat_customer_obj = LiveChatCustomer.objects.get(
                    pk=livechat_guest_agent_audit)
                guest_agent_group_chat_duration += livechat_customer_obj.group_chat_duration

            if guest_agent_group_chat_duration != 0:
                group_interaction_duration = guest_agent_group_chat_duration
            else:
                return "0s"

            hour = (group_interaction_duration) // 3600
            rem = (group_interaction_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            group_interaction_duration = ""
            if hour != 0:
                group_interaction_duration = str(hour) + "h "
            if minute != 0:
                group_interaction_duration += str(minute) + "m "
            group_interaction_duration += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error get_total_group_chat_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return group_interaction_duration

    def get_self_assigned_chat(self):

        if self.session_completed:
            livechat_self_assigned_chats = LiveChatCustomer.objects.filter(
                agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at, is_self_assigned_chat=True)
        else:
            livechat_self_assigned_chats = LiveChatCustomer.objects.filter(
                agent_id=self.user, joined_date__gte=self.session_starts_at, is_self_assigned_chat=True)

        return livechat_self_assigned_chats.count()
    
    def get_average_first_time_response_time(self):
        average_first_time_response = "NR"
        try:

            if self.session_completed:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at, agent_first_time_response_time__isnull=False)
            else:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, agent_first_time_response_time__isnull=False)

            average_first_time_response = livechat_customer_objs.aggregate(
                Sum('agent_first_time_response_time'))['agent_first_time_response_time__sum']

            if average_first_time_response == None or average_first_time_response == "None":
                return "NR"

            customer_count = livechat_customer_objs.count()
            average_first_time_response = average_first_time_response // customer_count
            hour = (average_first_time_response) // 3600
            rem = (average_first_time_response) % 3600
            minute = rem // 60
            sec = rem % 60
            average_first_time_response = ""
            if hour != 0:
                average_first_time_response = str(hour) + "h "
            if minute != 0:
                average_first_time_response += str(minute) + "m "
            average_first_time_response += str(sec) + "s"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_average_first_time_response_time %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return average_first_time_response
    
    def get_no_response_count(self):
        no_response_count = 0
        try:

            if self.session_completed:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at, agent_first_time_response_time__isnull=True)
            else:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, agent_first_time_response_time__isnull=True)

            if livechat_customer_objs == None or livechat_customer_objs == "None":
                return 0
            else:
                return livechat_customer_objs.count()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in no_response_count %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return no_response_count

    def get_average_nps(self):
        average_nps = 0
        try:
            if self.session_completed:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at, joined_date__lte=self.session_ends_at).exclude(rate_value=-1)
            else:
                livechat_customer_objs = LiveChatCustomer.objects.filter(
                    agent_id=self.user, joined_date__gte=self.session_starts_at).exclude(rate_value=-1)

            if not livechat_customer_objs:
                return 0
            else:
                customer_count = livechat_customer_objs.count()
                average_nps = livechat_customer_objs.aggregate(Sum('rate_value'))['rate_value__sum']
                if (average_nps % customer_count) == 0:
                    average_nps = int(average_nps / customer_count)
                    return average_nps
                else:
                    average_nps = "{:.1f}".format((average_nps / customer_count))
                    return average_nps

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_average_nps %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return average_nps


class LiveChatVideoConferencing(models.Model):

    meeting_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique meeting id for each video conferencing session')

    agent = models.ForeignKey('LiveChatUser', on_delete=models.CASCADE, null=True, blank=True,
                              help_text='Agent who generated video conferencing link')

    full_name = models.CharField(max_length=100, null=True, blank=True)

    mobile_number = models.CharField(max_length=100, null=True, blank=True)

    meeting_description = models.CharField(
        max_length=2048, null=True, blank=True)

    meeting_start_date = models.DateField(null=True, blank=True)

    meeting_start_time = models.TimeField(null=True, blank=True)

    meeting_end_time = models.TimeField(null=True, blank=True)

    meeting_password = models.CharField(max_length=2048, null=True, blank=True)

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.meeting_id) + " - " + str(self.full_name)

    class Meta:
        verbose_name = 'LiveChatVideoConferencing'
        verbose_name_plural = 'LiveChatVideoConferencing'


class LiveChatAdminConfig(models.Model):

    admin = models.ForeignKey('LiveChatUser', on_delete=models.CASCADE, null=True, blank=True,
                              help_text='Admin, for whom configuration to be set')

    is_video_meeting_enabled = models.BooleanField(default=True)

    livechat_config = models.ManyToManyField(
        LiveChatConfig, blank=True, help_text="LiveChatConfig for every bot")

    livechat_theme_color = models.CharField(
        max_length=2048, default="39,85,203", null=True, blank=True)

    show_version_footer = models.BooleanField(
        default=True, help_text="if True, it will show version footer.")
    canned_response_config = models.CharField(max_length=50, blank=True, default="<>()\"/;:^'",
                                              help_text='Characters which are not allowed in CannedResponse')

    agent_message_config = models.CharField(max_length=50, blank=True, default="\-\+,#!",
                                            help_text='Characters which are not allowed in agent message')

    is_livechat_only_admin_enabled = models.BooleanField(
        default=False, help_text="Designates whether livechat only admin feature is enabled or not")

    is_email_notification_enabled = models.BooleanField(
        default=False, help_text="Designates whether admin has enabled email notification")

    chat_history_refresh_interval = models.IntegerField(
        default=15, help_text="Time interval in which chat history page should refresh (in seconds)")

    is_self_assign_chat_agent_enabled = models.BooleanField(
        default=False, help_text="Designates whether admin has enabled self assign options for agents")

    is_supervisor_allowed_to_create_group = models.BooleanField(default=False)
    
    allow_supervisor_to_add_supervisor = models.BooleanField(default=False, help_text="Designates whether supervisor is allowed to add other supervisor in a group chat.")

    group_size_limit = models.IntegerField(default=100)

    is_chat_termination_analytics_enabled = models.BooleanField(default=True, help_text="Designates whether chat termination analytics feature is enabled")

    is_chat_escalation_matrix_enabled = models.BooleanField(
        default=False, help_text="Designates whether chat escalation matrix for customers is enabled.")

    is_agent_allowed_to_force_report = models.BooleanField(
        default=False, help_text="Designates whether agent can force report a customer.")

    warning_text_for_customer = models.TextField(
        default="WARNING: Please refrain from using Abusive texts, otherwise the chat will be disconnected.", 
        null=True, blank=True, help_text="This text will be shown to customer while warning him for using blacklisted keyword/s.")

    end_chat_text_for_reported_customer = models.TextField(
        default="Due to indecent behavior chat has been disconnected.", 
        null=True, blank=True, help_text="This text will be shown to customer while reporting him.")

    is_agent_analytics_enabled = models.BooleanField(
        default=True, help_text="Designates whether agent side analytics is enabled.")

    is_special_character_allowed_in_chat = models.BooleanField(
        default=True, help_text="Designates whether special character is allowed for chat during a livechat session.")

    is_special_character_allowed_in_file_name = models.BooleanField(
        default=False, help_text="Designates whether special character is allowed for file names during a livechat session.")
    
    max_users_allowed_to_be_created = models.IntegerField(
        default=100,
        help_text="Defines the upper cap on the total no. of active agents and supervisor, which can be created under a Livechat admin")    
    
    kafka_error_email_list = models.TextField(
        default='[]', null=True, blank=True, help_text="If something goes wrong in the Kafka producer then the error would be sent to these emails. Format of entering the email IDs is - ['abc@email.com', 'def@email.com']")
    
    def __str__(self):
        return str(self.admin.user.username)

    def get_livechat_theme_lighten_one(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",1)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_one no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        return RGB_25_103_210_01

    def get_livechat_theme_lighten_two(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",0.1)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_one no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return RGB_25_103_210_01

    def get_livechat_theme_lighten_three(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",0.08)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_one no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return RGB_25_103_210_01

    def get_livechat_theme_lighten_four(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",0.03)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_one no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return RGB_25_103_210_01

    def get_livechat_theme_lighten_five(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",0.8)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_one no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return RGB_25_103_210_01

    def get_livechat_theme_lighten_six(self):
        try:
            return "rgb(" + str(self.livechat_theme_color) + ",0.5)"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_livechat_theme_lighten_six no such theme %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return RGB_25_103_210_01

    class Meta:
        verbose_name = 'LiveChatAdminConfig'
        verbose_name_plural = 'LiveChatAdminConfig'


@receiver(post_save, sender=LiveChatAdminConfig)
def set_livechat_admin_config_obj_cache(sender, instance, **kwargs):
    livechat_config_objs = instance.livechat_config.all()
    for livechat_config_obj in livechat_config_objs:
        cache.set("LiveChatAdminConfig_" + str(livechat_config_obj.bot.pk), instance, settings.CACHE_TIME)


class LiveChatConsoleColour(models.Model):
    main_colour = models.TextField(default="#0254D7")
    background_colour = models.TextField(default="#F8FAFF")
    user_message_colour = models.TextField(default=" #0A68FF")

    class Meta:
        verbose_name = 'LiveChatConsoleColour'
        verbose_name_plural = 'LiveChatConsoleColour'


class LiveChatFileAccessManagement(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique access token key')

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    is_public = models.BooleanField(default=False)

    file_access_type = models.CharField(
        max_length=256, default="all", null=True, blank=True, choices=FILE_ACCESS_TYPES, help_text="Indicates the file access type.")

    group = models.ForeignKey(
        'LiveChatInternalChatGroup', on_delete=models.SET_NULL, null=True, blank=True)

    user_group = models.ForeignKey(
        'LiveChatInternalUserGroup', on_delete=models.SET_NULL, null=True, blank=True)

    users = models.ManyToManyField(
        'LiveChatUser', blank=True, related_name="users", help_text='LiveChatUsers who can access the file.')    

    is_public_to_all_user = models.BooleanField(default=False, help_text='Indicates all user can access the file.')

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when access management object is created')
    
    is_mailer_report = models.BooleanField(
        default=False, help_text="Designates whether the file is LiveChat Mailer Report File")
    
    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.is_public)

    class Meta:
        verbose_name = 'LiveChatFileAccessManagement'
        verbose_name_plural = 'LiveChatFileAccessManagement'

    def is_obj_time_limit_exceeded(self):
        try:
            import pytz
            time_zone = pytz.timezone(settings.TIME_ZONE)

            created_datetime = self.created_datetime.astimezone(
                time_zone)
            current_datetime = timezone.now().astimezone(time_zone)

            if (current_datetime - created_datetime).total_seconds() >= (FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT_LIVECHAT * 60 * 60):
                return True

            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in is_obj_time_limit_exceeded for LiveChatFileAccessManagement %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
            return True


class LiveChatDeveloperProcessor(models.Model):
    name = models.CharField(default="",
                            max_length=100, help_text="Function name")

    function = models.TextField(
        default="def f(x):\n    return x", null=True, blank=True, help_text="Function code")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'LiveChatDeveloperProcessor'
        verbose_name_plural = 'LiveChatDeveloperProcessor'


class LiveChatProcessors(models.Model):
    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=False, blank=False)

    end_chat_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="End chat processor", related_name="EndChatProcessor")

    show_customer_details_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Customer detail processor")

    assign_agent_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="Assign agent processor", related_name="AssignAgentProcessor")

    push_api = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="LiveChat Push API", related_name="LiveChatPushAPI")

    raise_ticket_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="LiveChat raise ticket processor", related_name="RaiseTicketProcessor")

    search_ticket_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="LiveChat search ticket processor", related_name="SearchTicketProcessor")

    get_previous_tickets_processor = models.ForeignKey(
        LiveChatDeveloperProcessor, on_delete=models.SET_NULL, blank=True, null=True, help_text="LiveChat get previous tickets processor", related_name="GetPreviousTicketsProcessor")

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'Processors'
        verbose_name_plural = 'Processors'


class LiveChatPIIDataToggle(models.Model):
    user = models.ForeignKey(
        'LiveChatUser', on_delete=models.CASCADE, null=False, blank=False)
    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=False, blank=False)
    otp = models.CharField(max_length=200)
    token = models.UUIDField(default=uuid.uuid4,
                             editable=False)
    is_expired = models.BooleanField(default=True, null=False, blank=False)

    def __str__(self):
        return str(self.user.user.username)

    class Meta:
        verbose_name = 'LiveChatPIIDataToggle'
        verbose_name_plural = 'LiveChatPIIDataToggle'


class LiveChatGuestAgentAudit(models.Model):
    livechat_customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                          on_delete=models.CASCADE, db_index=True)
    livechat_agent = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.CASCADE,
                                       related_name="action_performed_by", help_text="Agent id who has performed the action")
    action = models.TextField(
        default="", null=True, blank=True, help_text="What action was performed by/for guest agent")
    action_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when of action was performed.")

    def __str__(self):
        return str(self.livechat_customer.session_id)

    class Meta:
        verbose_name = "LiveChatGuestAgentAudit"
        verbose_name_plural = "LiveChatGuestAgentAudit"


class LiveChatInternalMISDashboard(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, unique=True,
                                  editable=False, db_index=True, help_text='unique message id')

    sender_name = models.CharField(max_length=100, default="user", blank=True, null=True,
                                   help_text="designates wheter it is a user message or system message")

    sender = models.ForeignKey(
        'LiveChatUser', related_name='message_sender', on_delete=models.SET_NULL, null=True, blank=True)

    receiver = models.ForeignKey(
        'LiveChatUser', related_name='message_receiver', on_delete=models.SET_NULL, null=True, blank=True)

    group = models.ForeignKey(
        'LiveChatInternalChatGroup', on_delete=models.SET_NULL, null=True, blank=True)

    user_group = models.ForeignKey(
        'LiveChatInternalUserGroup', on_delete=models.SET_NULL, null=True, blank=True)

    message_info = models.ForeignKey(
        'LiveChatInternalMessageInfo', on_delete=models.SET_NULL, null=True, blank=True)

    message_date = models.DateField(default=now, db_index=True)

    message_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when message was sent")

    is_message_seen = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether message is read or not")

    def __str__(self):
        return str(self.sender.user.username) + " - " + str(self.pk)

    class Meta:
        verbose_name = 'LiveChatInternalMISDashboard'
        verbose_name_plural = 'LiveChatInternalMISDashboard'


class LiveChatInternalMessageInfo(models.Model):
    message_text = models.TextField(
        default="", null=True, blank=True, help_text="Message received or sent")

    attached_file_src = models.TextField(
        default="", null=True, blank=True, help_text="Path of attachment file")

    attached_file_name = models.TextField(
        default="", null=True, blank=True, help_text="Name of attachment file")

    thumbnail_file_src = models.TextField(
        default="", null=True, blank=True, help_text="Path of attachment file thumbnail")

    preview_file_src = models.TextField(
        default="", null=True, blank=True, help_text="Path of attachment file preview")

    is_replied_message = models.BooleanField(
        default=False, help_text="Designates whether it is a replied message")

    reply_message_text = models.TextField(
        default="", null=True, blank=True, help_text="Replied message")

    reply_attached_file_src = models.TextField(
        default="", null=True, blank=True, help_text="Path of replied message attachment file")

    reply_attached_file_name = models.TextField(
        default="", null=True, blank=True, help_text="Name of replied message attachment file")

    reply_thumbnail_file_src = models.TextField(
        default="", null=True, blank=True, help_text="Path of replied message attachment file thumbnail")

    reply_message_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when of message")

    def __str__(self):
        return str(self.message_text) + " " + str(self.attached_file_name)

    class Meta:
        verbose_name = 'LiveChatInternalMessageInfo'
        verbose_name_plural = 'LiveChatInternalMessageInfo'


class LiveChatInternalChatGroup(models.Model):
    group_id = models.UUIDField(default=uuid.uuid4,
                                unique=True, editable=False, db_index=True, help_text='unique group id')

    group_name = models.CharField(max_length=200, help_text="Name of group")

    group_description = models.TextField(
        default="", null=True, blank=True, help_text="Description of group")

    icon_path = models.TextField(
        default="", null=True, blank=True, help_text="File path of group icon")

    members = models.ManyToManyField(
        'LiveChatInternalChatGroupMembers', blank=True, related_name="members", help_text='Members of the group')

    created_by = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True)

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when group was created")

    last_updated_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when group details were last updated")

    is_deleted = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether group is deleted or not")

    delete_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when group was deleted")

    is_removed = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether group is removed from display or not")

    removed_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when group was removed")
    
    last_msg_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time of last message sent in this group")

    def __str__(self):
        return str(self.group_name)

    class Meta:
        verbose_name = 'LiveChatInternalChatGroup'
        verbose_name_plural = 'LiveChatInternalChatGroups'


class LiveChatInternalGroupActivity(models.Model):
    group = models.ForeignKey(
        'LiveChatInternalChatGroup', on_delete=models.SET_NULL, null=True, blank=True)

    performed_by = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True, help_text='User who performed the activity')

    activity_performed = models.CharField(
        max_length=256, null=True, blank=True, choices=GROUP_ACTIVITIES)

    activity_performed_details = models.TextField(
        default="", null=True, blank=True, help_text="Performed activity details")

    activity_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when activity was performed")

    def __str__(self):
        return str(self.performed_by.user.username) + '-' + str(self.activity_performed)

    class Meta:
        verbose_name = 'LiveChatInternalGroupActivity'
        verbose_name_plural = 'LiveChatInternalGroupActivity'


class LiveChatInternalMessageReceipt(models.Model):
    user = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True)

    mis_data = models.ForeignKey(
        'LiveChatInternalMISDashboard', on_delete=models.SET_NULL, null=True, blank=True)

    group = models.ForeignKey(
        'LiveChatInternalChatGroup', on_delete=models.SET_NULL, null=True, blank=True)

    is_message_read = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether the message is read or not")

    read_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when message was read")

    def __str__(self):
        return str(self.user.user.username)

    class Meta:
        verbose_name = 'LiveChatInternalMessageReceipt'
        verbose_name_plural = 'LiveChatInternalMessageReceipt'


class LiveChatInternalChatGroupMembers(models.Model):
    member_id = models.UUIDField(default=uuid.uuid4, unique=True,
                                 editable=False, db_index=True, help_text='unique member id')

    user = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True)

    group = models.ForeignKey(
        'LiveChatInternalChatGroup', on_delete=models.SET_NULL, null=True, blank=True)

    is_removed = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether this member is removed from group or not")

    is_deleted = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether this member has deleted this group or not")

    has_left = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether this member has left this group or not")

    remove_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user was removed from group")

    delete_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user deleted the group")

    left_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user left the group")

    def __str__(self):
        return str(self.user) + '-' + str(self.is_removed)

    class Meta:
        verbose_name = 'LiveChatInternalChatGroupMembers'
        verbose_name_plural = 'LiveChatInternalChatGroupMembers'


class LiveChatInternalUserGroup(models.Model):
    group_id = models.UUIDField(default=uuid.uuid4,
                                unique=True, editable=False, db_index=True, help_text='unique group id')

    members = models.ManyToManyField(
        'LiveChatUser', blank=True, related_name="members", help_text='Members of the group')

    chat_belong_to = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True, help_text="Designates which user's chat is converted into a group")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when user group was created")

    last_updated_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when new members were last added")
    
    is_converted_into_group = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether this chat is converted into group or not")

    last_msg_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time of last message sent in this group")

    is_chat_started = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether this chat is started or not")

    def __str__(self):
        return str(self.group_id)

    class Meta:
        verbose_name = 'LiveChatInternalUserGroup'
        verbose_name_plural = 'LiveChatInternalUserGroups'


class LiveChatEmailProfile(models.Model):

    livechat_user = models.ForeignKey(
        'LiveChatUser', on_delete=models.SET_NULL, null=True, blank=True, help_text='Livechat User under which this mail profile belongs to')

    profile_name = models.TextField(
        null=False, blank=False, help_text='Unique name of the profile')

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mail profile is created')

    last_updated_datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when mail profile was last updated')

    email_frequency = models.TextField(
        default="[]", null=False, blank=False)

    email_address = models.TextField(
        default="[]", null=True, blank=True)

    email_subject = models.TextField(
        default="COGNO AI - LiveChat Report Mailer", null=True, blank=True)

    agent_connection_rate = models.TextField(
        default="0", null=True, blank=True)

    is_table_parameters_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether tabular data is enabled for this email profile")

    table_parameters = models.ForeignKey(
        'LiveChatEmailTableParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_graph_parameters_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether graphical data is enabled for this email profile")

    graph_parameters = models.ForeignKey(
        'LiveChatEmailGraphParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_attachment_parameters_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether attahcment report is enabled for this email profile")

    attachment_parameters = models.ForeignKey(
        'LiveChatEmailAttachmentParameters', null=True, blank=True, on_delete=models.SET_NULL)

    is_deleted = models.BooleanField(
        default=False, null=False, blank=False)

    def __str__(self):
        return str(self.profile_name)

    class Meta:
        verbose_name = 'LiveChatEmailProfile'
        verbose_name_plural = 'LiveChatEmailProfile'

    def get_email_list(self):
        return json.loads(self.email_address)


class LiveChatEmailTableParameters(models.Model):

    profile = models.ForeignKey(
        'LiveChatEmailProfile', blank=True, null=True, on_delete=models.SET_NULL)

    count_variation = models.TextField(
        default="['1']", null=True, blank=True, help_text="Date range for tabular data")

    channel = models.TextField(
        default="[]", null=True, blank=True)

    table_records = models.TextField(
        default="[]", null=True, blank=True, help_text="Records to be included in tabular data")

    def __str__(self):
        profile_name = DELETE_PROFILE
        if self.profile:
            profile_name = self.profile.profile_name
        return profile_name

    class Meta:
        verbose_name = 'LiveChatEmailTableParameters'
        verbose_name_plural = 'LiveChatEmailTableParameters'


class LiveChatEmailGraphParameters(models.Model):

    profile = models.ForeignKey(
        'LiveChatEmailProfile', blank=True, null=True, on_delete=models.SET_NULL)

    is_graph_chart_reports_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether graphical chart reports data is enabled for this email profile")

    graph_chart_reports = models.TextField(
        default="[]", null=True, blank=True, help_text="Records to be included in graphical chart reports data")

    is_graph_interaction_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether graphical interaction per chat data is enabled for this email profile")

    is_graph_avg_handle_time_enabled = models.BooleanField(
        default=False, null=False, blank=False, help_text="Designates whether graphical average handle time data is enabled for this email profile")

    def __str__(self):
        profile_name = DELETE_PROFILE
        if self.profile:
            profile_name = self.profile.profile_name
        return profile_name

    class Meta:
        verbose_name = 'LiveChatEmailGraphParameters'
        verbose_name_plural = 'LiveChatEmailGraphParameters'


class LiveChatEmailAttachmentParameters(models.Model):

    profile = models.ForeignKey(
        'LiveChatEmailProfile', blank=True, null=True, on_delete=models.SET_NULL)

    attachment_parameters = models.TextField(
        default="[]", null=True, blank=True, help_text="Designates which attachment reports are to be included for this mail profile")

    def __str__(self):
        profile_name = DELETE_PROFILE
        if self.profile:
            profile_name = self.profile.profile_name
        return profile_name

    class Meta:
        verbose_name = 'LiveChatEmailAttachmentParameters'
        verbose_name_plural = 'LiveChatEmailAttachmentParameters'


class LiveChatMailerAuditTrail(models.Model):

    profile = models.ForeignKey(
        'LiveChatEmailProfile', null=True, blank=True, on_delete=models.SET_NULL)

    email_frequency = models.TextField(default="", null=True, blank=True)

    sent_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        profile_name = DELETE_PROFILE
        if self.profile:
            profile_name = self.profile.profile_name
        return profile_name

    class Meta:
        verbose_name = 'LiveChatMailerAuditTrail'
        verbose_name_plural = 'LiveChatMailerAuditTrail'


class LiveChatDisposeChatForm(models.Model):
    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=False, blank=False)

    is_form_enabled = models.BooleanField(
        default=False, help_text="Designates whether form is enabled or not.")

    form = models.TextField(default="{}", null=True, blank=True,
                            help_text='Form fields info in json format.')

    edited_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'LiveChatDisposeChatForm'
        verbose_name_plural = 'LiveChatDisposeChatForm'


class LiveChatVoIPData (models.Model):
    meeting_id = models.UUIDField(default=uuid.uuid4, unique=True,
                                  editable=False, db_index=True, help_text='unique meeting id')

    call_type = models.CharField(
        max_length=256, null=True, blank=True, choices=CALL_TYPE, help_text="Designates whether call type is PIP or New Tab")

    customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                 on_delete=models.SET_NULL)

    agent = models.ForeignKey('LiveChatUser', null=True, blank=True,
                              on_delete=models.SET_NULL)

    initiated_by = models.CharField(
        max_length=256, null=True, blank=True, choices=VOIP_INITIATOR, help_text="Designates whether call is initiated by customer or agent.")

    request_datetime = models.DateTimeField(default=timezone.now)

    is_accepted = models.BooleanField(
        default=False, help_text="Designates whether call is accepted by user or not.")

    is_rejected = models.BooleanField(
        default=False, help_text="Designates whether call is rejected by user or not.")

    is_started = models.BooleanField(
        default=False, help_text="Designates whether call is started or not.")

    start_datetime = models.DateTimeField(default=timezone.now)

    end_datetime = models.DateTimeField(default=timezone.now)

    is_completed = models.BooleanField(
        default=False, help_text="Designates whether call is completed or not.")

    is_interrupted = models.BooleanField(
        default=False, help_text="Designates whether call is interrupted by user or not.")

    call_recording = models.CharField(
        max_length=4096, null=True, blank=True)
    
    video_recording = models.CharField(
        max_length=4096, null=True, blank=True)
    
    agent_recording_start_time = models.DateTimeField(default=timezone.now, help_text="Video recording start time at agent's side")

    is_merging_done = models.BooleanField(
        default=False, help_text="Designates whether audio merging is done or not.")

    merged_file_path = models.CharField(
        max_length=4096, null=True, blank=True)
    
    rating = models.IntegerField(
        default=-1, help_text="This much rating is given to the agent by the customer at the end of the video call.")

    text_feedback = models.TextField(default="", null=True, blank=True)
    
    is_rating_given = models.BooleanField(
        default=False, help_text="Designates whether rating is given by customer or not.")

    def __str__(self):
        return str(self.meeting_id) + '-' + self.agent.user.username

    def get_call_duration(self):
        try:
            call_duration = (self.end_datetime - self.start_datetime).seconds
            hour = (call_duration) // 3600
            rem = (call_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            if sec != 0:
                time += str(sec) + "s"
            return time
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_call_duration for LiveChatVOIPData %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return "0s"

    class Meta:
        verbose_name = 'LiveChatVoIPData'
        verbose_name_plural = 'LiveChatVoIPData'

    def get_duration(self):
        try:
            return (self.end_datetime - self.start_datetime).total_seconds()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_total_duration %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            return 0


class LiveChatWhatsAppServiceProvider(models.Model):

    name = models.CharField(max_length=20, null=False, blank=False,
                            choices=WSP_CHOICES, help_text="Name of WhatsApp Service Provider")

    default_code_file_path = models.TextField(
        null=True, blank=True, help_text="Default code file path of the Whatsapp Service Provider")

    def __str__(self):
        # This method is defined by django itself.
        # This will return name associated with WSP_CHOICES value. (Format - get_{attribut_name}_display)
        return str(self.get_name_display())

    class Meta:
        verbose_name = 'LiveChatWhatsAppServiceProvider'
        verbose_name_plural = 'LiveChatWhatsAppServiceProviders'


class MSDynamicsIntegration(models.Model):

    integration_url = models.TextField(
        null=True, blank=True, help_text="Microsoft Dynamics environment url")

    class Meta:
        verbose_name = 'MSDynamicsIntegration'
        verbose_name_plural = 'MSDynamicsIntegration'


class LiveChatIntegrations(models.Model):

    admin = models.ForeignKey('LiveChatUser', on_delete=models.CASCADE, null=True, blank=True,
                              help_text='Admin, for whom configuration to be set')

    ms_dynamics_config = models.ForeignKey('MSDynamicsIntegration', on_delete=models.CASCADE, null=True, blank=True,
                                           help_text='Admin, for whom configuration to be set')


class LiveChatTranslationCache(models.Model):
    input_text_hash_data = models.TextField(
        default="", db_index=True, help_text="md5 hash")

    input_text = models.TextField(default="", help_text="User's text")

    translated_data = models.TextField(
        default="", help_text="text after translation")

    lang = models.CharField(max_length=10, default="en",
                            null=True, help_text="Language")

    def __str__(self):
        return str(self.translated_data)

    class Meta:
        verbose_name = 'LiveChatTranslationCache'
        verbose_name_plural = 'LiveChatTranslationCache'


class LiveChatRaiseTicketForm(models.Model):
    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=False, blank=False)

    is_form_enabled = models.BooleanField(
        default=False, help_text="Designates whether form is enabled or not.")

    form = models.TextField(default="{}", null=True, blank=True,
                            help_text='Form fields info in json format.')

    edited_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'LiveChatRaiseTicketForm'
        verbose_name_plural = 'LiveChatRaiseTicketForm'


class LiveChatTicketAudit(models.Model):

    customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                          on_delete=models.CASCADE)

    agent = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.CASCADE, help_text="Agent id who raised the ticket")
    
    ticket_id = models.TextField(default="", null=True, blank=True)

    action_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when ticket was raised.")

    def __str__(self):
        return str(self.customer.session_id)

    class Meta:
        verbose_name = "LiveChatTicketAudit"
        verbose_name_plural = "LiveChatTicketAudit"


class LiveChatCobrowsingData (models.Model):
    meeting_id = models.UUIDField(default=uuid.uuid4, unique=True,
                                  editable=False, db_index=True, help_text='unique meeting id')
    
    cobrowse_session_id = models.CharField(default="", null=True, blank=True, max_length=100, help_text='cobrowse session id')

    customer = models.ForeignKey('LiveChatCustomer', null=True, blank=True,
                                 on_delete=models.SET_NULL)

    agent = models.ForeignKey('LiveChatUser', null=True, blank=True,
                              on_delete=models.SET_NULL)

    guest_agents = models.ManyToManyField(
        'LiveChatUser', related_name="guest_agents_joined", blank=True, help_text="Guest agents who have joined the cobrowsing session")

    request_datetime = models.DateTimeField(default=timezone.now)

    is_accepted = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing request is accepted by user or not.")

    is_rejected = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing request is rejected by user or not.")

    is_started = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing is started or not.")

    start_datetime = models.DateTimeField(default=timezone.now)

    end_datetime = models.DateTimeField(default=timezone.now)

    is_completed = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing is completed or not.")
    
    is_notification_displayed = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing end notification is shown to customer or not.")

    is_interrupted = models.BooleanField(
        default=False, help_text="Designates whether cobrowsing is interrupted by user or not.")
    
    rating = models.IntegerField(
        default=-1, help_text="Rating given to the agent by the customer at the end of the cobrowsing session.")

    text_feedback = models.TextField(default="", null=True, blank=True,
                                     help_text="Comments given to the agent by the customer at the end of the cobrowsing session.")

    def __str__(self):
        return str(self.meeting_id) + '-' + self.agent.user.username

    def get_duration(self):
        try:
            cobrowsing_duration = (self.end_datetime - self.start_datetime).seconds
            hour = (cobrowsing_duration) // 3600
            rem = (cobrowsing_duration) % 3600
            minute = rem // 60
            sec = rem % 60
            time = ""
            if hour != 0:
                time = str(hour) + "h "
            if minute != 0:
                time += str(minute) + "m "
            if sec != 0:
                time += str(sec) + "s"
            return time
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error in get_duration for LiveChatCobrowsingData %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

            return "0s"

    def get_duration_in_seconds(self):
        try:
            return (self.end_datetime - self.start_datetime).total_seconds()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("get_total_duration_in_seconds %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            return 0

    class Meta:
        verbose_name = 'LiveChatCobrowsingData'
        verbose_name_plural = 'LiveChatCobrowsingData'


class LiveChatFollowupCustomer(models.Model):

    livechat_customer = models.ForeignKey('LiveChatCustomer', null=False, blank=False, on_delete=models.CASCADE)

    agent_id = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.CASCADE, help_text="Agent")

    assigned_date = models.DateTimeField(default=timezone.now, help_text="Date and time when follow up lead was assigned")

    source = models.TextField(default="", null=True, blank=True, help_text="Source of this follow up lead")

    is_completed = models.BooleanField(default=False, help_text="Designated whether follow up lead is completed")

    completed_date = models.DateTimeField(default=timezone.now, help_text="Date and time when follow up lead was completed")

    is_whatsapp_conversation_reinitiated = models.BooleanField(default=False,
                                                               help_text="Designates whether conversation is reinitiated for followup lead. Applicable for whatsapp channel only.")

    followup_count = models.IntegerField(
        default=1, help_text="Designates the count of how many times a lead was not assigned a agent after going into assignment function.")

    def __str__(self):
        return str(self.livechat_customer.session_id)

    class Meta:
        verbose_name = "LiveChatFollowupCustomer"
        verbose_name_plural = "LiveChatFollowupCustomer"  

    def get_lead_source(self):
        source = ""
        try:

            source_split = self.source.split('_')
            source = source_split[0].title() + ' ' + source_split[1].title()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get_lead_source %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        return source

    def get_masked_mobile_number(self):
        mobile_number = self.livechat_customer.phone
        masked_mobile_number = "xxxxxxxxxx"
        try:

            masked_mobile_number = mobile_number[0:2] + "xx" + mobile_number[4:6] + "xx" + mobile_number[8:10]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Problem occured in Livechat get_masked_mobile_number %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})
        return masked_mobile_number


class LiveChatReportedCustomer(models.Model):

    livechat_customer = models.ForeignKey('LiveChatCustomer', null=False, blank=False, on_delete=models.CASCADE)

    created_date = models.DateTimeField(default=timezone.now, help_text="Date and time when customer was warned")

    is_reported = models.BooleanField(default=False, help_text="Designates whether customer is reported")

    reported_date = models.DateTimeField(default=timezone.now, help_text="Date and time when customer was reported")

    is_blocked = models.BooleanField(default=False, help_text="Designates whether customer is blocked")

    blocked_date = models.DateTimeField(default=timezone.now, help_text="Date and time when customer was blocked")

    is_completed = models.BooleanField(default=False, help_text="Designates whether customer was ignored/unblocked from reported/blocked customers page")

    block_duration = models.CharField(max_length=256, default="", null=True, blank=True, choices=CUSTOMER_BLOCK_DURATION)

    chat_escalation_report_ignored_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when customer lastly ignored report notification.")

    def __str__(self):
        return str(self.livechat_customer.session_id)

    class Meta:
        verbose_name = "LiveChatReportedCustomer"
        verbose_name_plural = "LiveChatReportedCustomer"


class LiveChatEmailConfig(models.Model):

    admin_config = models.ForeignKey('LiveChatAdminConfig', on_delete=models.CASCADE, null=False, blank=False,
                                     help_text='Admin config for which email configuration is set')

    is_livechat_enabled_for_email = models.BooleanField(
        default=False, help_text="Designates whether livechat is enabled through email channel.")

    is_auto_disposal_enabled = models.BooleanField(
        default=False, help_text="Designates whether livechat auto disposal is enabled through email channel.")

    is_session_inactivity_enabled = models.BooleanField(
        default=False, help_text="Designates whether session inactivity for livechat auto disposal is enabled through email channel.")

    chat_disposal_duration = models.IntegerField(
        default=1, help_text="Duration in days after which chat would get disposed.")

    is_followup_leads_over_mail_enabled = models.BooleanField(
        default=False, help_text="Designates whether followup leads can chat over mail.")

    is_successful_authentication_complete = models.BooleanField(
        default=False, help_text="Designates whether email setup is configured successfully.")

    current_email_setup = models.ForeignKey('LiveChatEmailConfigSetup', on_delete=models.SET_NULL, null=True, blank=True,
                                            help_text='Current email setup used for this email config.')

    def __str__(self):
        return str(self.admin_config)

    class Meta:
        verbose_name = "LiveChatEmailConfig"
        verbose_name_plural = "LiveChatEmailConfig"


class LiveChatEmailConfigSetup(models.Model):

    admin_config = models.ForeignKey('LiveChatAdminConfig', on_delete=models.CASCADE, null=False, blank=False,
                                     help_text='Admin config for which email setup is done.')

    email = models.CharField(max_length=100, null=False,
                             blank=False, help_text="Email ID for email setup.")

    password = models.CharField(max_length=500, null=False,
                                blank=False, help_text="Password for email setup.")

    server = models.CharField(max_length=150, null=False,
                              blank=False, help_text="Server for email setup.")

    security = models.CharField(max_length=50, default="ssl",
                                null=True, blank=True, choices=EMAIL_SETUP_SECURITY)

    last_mail_uid = models.CharField(
        max_length=100, default="0", null=True, blank=True, help_text="Mail UID of last polled email.")

    def __str__(self):
        return str(self.email) + ' - ' + str(self.admin_config)

    class Meta:
        verbose_name = "LiveChatEmailConfigSetup"
        verbose_name_plural = "LiveChatEmailConfigSetup"


class LiveChatMISEmailData(models.Model):

    livechat_mis_obj = models.ForeignKey('LiveChatMISDashboard', on_delete=models.CASCADE, null=False, blank=False,
                                         help_text='LivechatMIS object for which email data is stored.')

    mail_uid = models.CharField(
        max_length=100, default="0", null=True, blank=True, help_text="Unique ID of each mail.")

    mail_message_id = models.TextField(
        default="", null=True, blank=True, help_text="Message ID is used to maintain mail threads.")

    mail_subject = models.TextField(
        default="", null=True, blank=True, help_text="Subject of the mail.")

    def __str__(self):
        return str(self.livechat_mis_obj)

    class Meta:
        verbose_name = "LiveChatMISEmailData"
        verbose_name_plural = "LiveChatMISEmailData"


class LiveChatInternalChatLastSeen(models.Model):

    user = models.ForeignKey('LiveChatUser', null=True, blank=True, on_delete=models.SET_NULL, help_text="User whose last seen time is being updated")

    last_seen = models.DateTimeField(default=timezone.now, help_text="Date and time when user was last seen in the chat")

    group = models.ForeignKey('LiveChatInternalChatGroup', null=True, blank=True, on_delete=models.SET_NULL, help_text="Group in which user's last seen time is updated")

    user_group = models.ForeignKey('LiveChatInternalUserGroup', null=True, blank=True, on_delete=models.SET_NULL, help_text="User Group in which user's last seen time is updated")

    def __str__(self):
        if self.group:
            return f'{str(self.user)} - {str(self.group)}'
        elif self.user_group:
            return f'{str(self.user)} - {str(self.user_group)}'
        else:
            return f'{str(self.user)}'

    class Meta:
        verbose_name = "LiveChatInternalChatLastSeen"
        verbose_name_plural = "LiveChatInternalChatLastSeen"  


class LiveChatAuthToken(models.Model):

    token = models.UUIDField(primary_key=True, default=uuid.uuid4,
                             editable=False, help_text='unique access token key')

    user = models.ForeignKey(
        'LiveChatUser', null=True, blank=False, on_delete=models.CASCADE, help_text='Foreign key of Livechat user to which the token belongs')

    is_expired = models.BooleanField(
        default=False, null=False, blank=False, help_text='Designates whether the token is expired or not.')

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when LiveChat Auth Token is created.")

    last_accessed_time = models.DateTimeField(
        default=timezone.now, help_text="Date and time when LiveChat Auth token was last used.")

    api_used_in_last_minute = models.IntegerField(
        default=1, null=True, blank=True, help_text="Number of times the external api is used in last minute. This field is for applying rate limiting.")

    def is_rate_limit_exceeded(self):
        if self.api_used_in_last_minute > RATE_LIMIT_FOR_EXTERNAL_API_IN_ONE_MINUTE:
            return True

        return False

    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name = 'LiveChatAuthToken'
        verbose_name_plural = 'LiveChatAuthTokens'


class LiveChatExternalAPIAuditTrail(models.Model):

    request_id = models.UUIDField(default=uuid.uuid4,
                                  editable=False, help_text='Request ID generated while accessing external API.')

    token = models.ForeignKey(
        'LiveChatAuthToken', null=True, on_delete=models.SET_NULL, help_text='Foreign key to auth token.')

    status_code = models.CharField(
        default="500", null=True, blank=True, help_text="Status code of the API Response sent to the user.", max_length=10)

    access_type = models.CharField(
        max_length=256, null=True, blank=True, choices=AUTH_TOKEN_ACCESS_TYPE_CHOICES, help_text="Type of data requested by user.")

    request_data = models.TextField(
        default="{}", null=True, blank=True, help_text="Request data received from API call.")

    response_data = models.TextField(
        default="{}", null=True, blank=True, help_text="API Response sent to the user.")

    metadata = models.TextField(
        default="{}", null=True, blank=True, help_text="Metadata of the request received.")

    created_datetime = models.DateTimeField(
        default=timezone.now, help_text="Date and time when external API is used.")

    def __str__(self):
        return str(self.request_id)

    class Meta:
        verbose_name = 'LiveChatExternalAPIAuditTrail'
        verbose_name_plural = 'LiveChatExternalAPIAuditTrails'


class LiveChatCronjobTracker(models.Model):

    cronjob_id = models.CharField(max_length=500, null=True, blank=True,
                                  help_text='a unique ID of the cronjob being executed')

    creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the cronjob tracker object was created')

    def __str__(self):
        try:
            return str(self.cronjob_id)
        except Exception:
            return "-"

    def is_object_expired(self):
        try:
            expiry_time_limit_in_seconds = CRONJOB_TRACKER_EXPIRY_TIME_LIMIT * 60
            total_time_elapsed = int((timezone.now() - self.creation_datetime).total_seconds())
            if total_time_elapsed >= expiry_time_limit_in_seconds:
                return True

            return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error in LiveChatCronjobTracker is_object_expired method %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            return False

    class Meta:
        verbose_name = 'LiveChatCronjobTracker'
        verbose_name_plural = 'LiveChatCronjobTracker'


class FusionAuditTrail(models.Model):

    user_id = models.CharField(max_length=100, help_text="EasyChat User ID.")

    bot_id = models.CharField(max_length=100, help_text="Bot ID.")

    request_packet = models.TextField(default="{\"items\":[]}",
                                      null=True, blank=True, help_text="Request Packet.")

    response_packet = models.TextField(default="{\"items\":[]}",
                                       null=True, blank=True, help_text="Response Packet.")

    created_at = models.DateTimeField(default=timezone.now)

    api_name = models.CharField(max_length=100, help_text="Name of the processor api.")

    api_status_code = models.CharField(default="200", max_length=100, help_text="API status code 200/300/500")

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = "FusionAuditTrail"
        verbose_name_plural = "FusionAuditTrail"
