# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django App
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete, pre_save
from django.db.models.functions import Length
from django.dispatch import receiver
from django.conf import settings
from django import template
import uuid


from EasyChatApp.models import *
from EasyTMSApp.utils import create_ticket_priority_obj, create_ticket_status_obj, get_agent_console_meta_data
from EasyTMSApp.constants import *

# Logger

import sys
import json
import logging
import string
import random

logger = logging.getLogger(__name__)


class WorkingCalendar(models.Model):

    date = models.DateField(null=True, blank=True)

    start_time = models.TimeField(null=True, blank=True)

    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return str(self.start_time) + " - " + str(self.end_time)

    class Meta:
        verbose_name = 'WorkingCalendar'
        verbose_name_plural = 'WorkingCalendars'


class LeaveCalendar(models.Model):

    leave_date_time = models.DateTimeField(null=True, blank=True)

    leave_reason = models.CharField(max_length=100, null=True, blank=True)

    is_approved = models.BooleanField(default=False)

    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + " - " + str(self.leave_reason)

    class Meta:
        verbose_name = 'LeaveCalendar'
        verbose_name_plural = 'LeaveCalendars'


class TicketCategory(models.Model):

    bot = models.ForeignKey('EasyChatApp.Bot', null=True,
                            blank=True, help_text="List of Bots created in EasyChat.", on_delete=models.SET_NULL,)

    ticket_category = models.CharField(
        max_length=200, null=True, blank=True, help_text="Name of ticket category.")

    ticket_period = models.IntegerField(
        null=True, blank=True, help_text="Number of days mapped with ticket category which helps to find resolution date of a ticket.")

    created_datetime = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Date and time when this ticket category")

    is_deleted = models.BooleanField(
        default=False, help_text="designates wheter the category deleted or not")

    def __str__(self):
        try:
            return str(self.ticket_category) + "-" + self.bot.bot_display_name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Error in naming: %s at %s",
                           str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
            return "Error in Name"

    class Meta:
        verbose_name = 'TicketCategory'
        verbose_name_plural = 'TicketCategories'


class Agent(models.Model):

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True, help_text="List of users created in EasyChat")

    agent_creation_datetime = models.DateTimeField(
        default=timezone.now, help_text='Datetime of when the agents account was created')

    role = models.CharField(max_length=10,
                              null=True,
                              blank=True,
                              choices=AGENT_ROLES,
                              default=AGENT_ROLES[2][0],
                              help_text='Status of a user where user can be "Manager" or "Agent".')

    level = models.CharField(max_length=10,
                              null=True,
                              blank=True,
                              choices=AGENT_LEVELS,
                              default=AGENT_LEVELS[0][0],
                              help_text='Status of a user where user can be "Manager" or "Agent".')

    agents = models.ManyToManyField(
        'Agent', blank=True)

    phone_number = models.CharField(
        max_length=50, null=True, blank=True, help_text="10 digit valid phone number of user")

    ticket_categories = models.ManyToManyField(
        'TicketCategory', blank=True, help_text='Agent can be assigned to specific ticket cateogries which will help to auto assign the ticket.')

    bots = models.ManyToManyField('EasyChatApp.Bot', blank=True, help_text='Agent can be assigned to specific bots which will help to auto assign the ticket.')

    is_absent = models.BooleanField(default=False)

    is_active = models.BooleanField(
        default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")

    is_account_active = models.BooleanField(
        default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")

    last_password_resend_date = models.DateField(
        default=timezone.now, help_text='Date when last time resend password was initiated')

    resend_password_count = models.IntegerField(
        default=RESEND_PASSWORD_THRESHOLD, help_text='Number of times resend password has been initiated in a day')

    console_meta_data = models.CharField(
        max_length=2048, default=json.dumps({"lead_data_cols": DEFAULT_LEAD_TABLE_COL}), null=True, blank=True)

    def get_bots(self):
        bot = ""
        try:
            bot_objs = self.bots.all().order_by(Length('name').asc())
            bot = ", ".join(
                [bot.name for bot in bot_objs])
            return bot
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_bots %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_ticket_categories(self):
        ticket_category = ""
        try:
            ticket_category_objs = self.ticket_categories.filter(is_deleted=False).order_by(Length('ticket_category').asc())
            ticket_category = ", ".join(
                [ticket_category.ticket_category for ticket_category in ticket_category_objs])
            return ticket_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_ticket_categories %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_bots_limited(self):
        try:
            max_length = 15
            bot_objs = self.bots.all().order_by(Length('name').asc())
            bot_all = ", ".join(
                [bot.name for bot in bot_objs])
            bot_all = bot_all.strip()

            bot = bot_all[:max_length]
            if bot.rfind(",") > 0:
                bot = bot[: bot.rfind(
                    ",")]

            if len(bot_all) > len(bot):
                return bot + ", ..."
            else:
                return bot
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_bots_limited %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_ticket_categories_limited(self):
        try:
            max_length = 15
            ticket_category_objs = self.ticket_categories.filter(is_deleted=False).order_by(Length('ticket_category').asc())
            ticket_category_all = ", ".join(
                [ticket_category.ticket_category for ticket_category in ticket_category_objs])
            ticket_category_all = ticket_category_all.strip()

            ticket_category = ticket_category_all[:max_length]
            if ticket_category.rfind(",") > 0:
                ticket_category = ticket_category[: ticket_category.rfind(
                    ",")]

            if len(ticket_category_all) > len(ticket_category):
                return ticket_category + ", ..."
            else:
                return ticket_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_ticket_categories_limited %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_ticket_categories_with_bot_name_html(self):
        ticket_category = ""
        try:
            ticket_category_objs = self.ticket_categories.filter(is_deleted=False).order_by(Length('ticket_category').asc())
            ticket_category = "".join(
                [ticket_category.ticket_category + " of " + ticket_category.bot.name + "<br>" for ticket_category in ticket_category_objs])
            return ticket_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_ticket_categories_with_bot_name_html %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def get_ticket_categories_with_bot_name(self):
        ticket_category = ""
        try:
            ticket_category_objs = self.ticket_categories.filter(is_deleted=False).order_by(Length('ticket_category').asc())
            ticket_category = "".join(
                [ticket_category.ticket_category + " of " + ticket_category.bot.name + "\n" for ticket_category in ticket_category_objs])
            return ticket_category
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_ticket_categories_with_bot_name %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'


@receiver(post_save, sender=Agent)
def create_access_token(sender, instance, **kwargs):
    if instance.role == "admin" and not kwargs["raw"]:
        access_token = TMSAccessToken.objects.filter(agent=instance).first()
        if access_token == None:
            TMSAccessToken.objects.create(agent=instance)


@receiver(post_save, sender=Agent)
def change_agent_settings(sender, instance, created, *args, **kwargs):
    if not kwargs["raw"] and created:
        console_meta_data = get_agent_console_meta_data(instance)
        instance.console_meta_data = console_meta_data
        instance.save()


class Ticket(models.Model):

    def generate_random_ticket_pk(self=None):
        size = 24
        chars = string.ascii_uppercase + string.digits
        ticket = ''.join(random.choice(chars) for _ in range(size))
        return ticket[:10]

    ticket_id = models.CharField(
        max_length=24, default=generate_random_ticket_pk, primary_key=True, editable=False, help_text="Unique 12 digit ticket id")

    access_token = models.ForeignKey(
        'TMSAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    agent = models.ForeignKey(
        'Agent', null=True, blank=True, on_delete=models.SET_NULL, help_text="Agent which is assigned to this ticket")

    issue_date_time = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Date and time when this ticket is generated")

    bot = models.ForeignKey('EasyChatApp.Bot', on_delete=models.SET_NULL, blank=True, null=True)

    bot_channel = models.ForeignKey(
        'EasyChatApp.Channel', null=True, blank=True, help_text="Channel from which ticket is generated.", on_delete=models.SET_NULL)

    query_description = models.TextField(
        default="", null=True, blank=True, help_text="Issue description entered by user")

    query_attachment = models.TextField(
        default='', null=True, blank=True, help_text="Issue attachments")

    ticket_category = models.ForeignKey(
        'TicketCategory', null=True, blank=True, on_delete=models.SET_NULL, help_text="Ticket category which will assigned to this ticket.")

    ticket_status = models.ForeignKey(
        'TicketStatus', null=True, blank=True, on_delete=models.SET_NULL)

    ticket_priority = models.ForeignKey(
        'TicketPriority', null=True, blank=True, on_delete=models.SET_NULL)

    is_resolved = models.BooleanField(
        default=False, help_text="Designates whether this issue is resolved or not.", db_index=True)

    resolved_date_time = models.DateTimeField(
        null=True, blank=True)

    customer_name = models.CharField(max_length=100, null=True, blank=True, help_text="Name of the user")

    customer_email_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Email of the user")

    customer_mobile_number = models.CharField(
        max_length=50, null=True, blank=True, help_text="Phone number of the user")

    customer_information = models.CharField(
        default='{"items": []}', max_length=2048, null=True, blank=True, help_text="Customer Extra Information")

    def __str__(self):
        return str(self.pk) + " - " + str(self.agent) + " - " + str(self.bot)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'


class TicketAuditTrail(models.Model):

    """
    ACTION_TYPE = (
        ("AGENT_ASSIGN", "Agent Assign"),
        ("STATUS_CHANGED", "Status Change"),
        ("PRIORITY_CHANGED", "Priority Change"),
        ("CATEGORY_CHANGED", "Category Changed"),
        ("AGENT_COMMENT", "Agent Comment"),
        ("RESOLVED_COMMENT", "Resolve Comment"),
        ("CUSTOMER_COMMENT", "Customers Comment"),
        ("CUSTOMER_ATTACHMENT", "Customers Attachment"),
    )
    """

    ticket = models.ForeignKey(
        Ticket, on_delete=models.SET_NULL, null=True, blank=True, help_text="Ticket category for which audit trail is created.")

    agent = models.ForeignKey(
        Agent, null=True, blank=True, on_delete=models.SET_NULL, help_text="Agent for whome audit trail is generated")

    action_type = models.CharField(max_length=100, null=False, blank=False)

    description = models.TextField(null=False, blank=False)

    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.ticket.ticket_id) + " - " + str(self.action_type) + " - " + str(self.description)

    class Meta:
        verbose_name = 'TicketAuditTrail'
        verbose_name_plural = 'TicketAuditTrails'


class AgentQuery(models.Model):

    agent = models.ForeignKey(
        Agent, null=True, blank=True, on_delete=models.SET_NULL, help_text="Agent who has created query")

    ticket = models.ForeignKey(
        Ticket, on_delete=models.SET_NULL, null=True, blank=True, help_text="Ticket category for which audit trail is created.")

    ticket_audit_trail = models.ForeignKey(
        TicketAuditTrail, on_delete=models.SET_NULL, null=True, blank=True, help_text="Ticket Audit Trail through which query was generated.")

    is_active = models.BooleanField(
        default=True, help_text="Designates whether this query is active or resolved.")

    extra_information = models.CharField(
        default='{"intent_id": ""}', max_length=2048, null=True, blank=True, help_text="Extra Information to process further")

    def __str__(self):
        return str(self.ticket.ticket_id) + " - " + str(self.agent) + " - " + str(self.is_active)

    class Meta:
        verbose_name = 'AgentQuery'
        verbose_name_plural = 'AgentQueries'


class TicketStatus(models.Model):

    name = models.CharField(max_length=2048)

    access_token = models.ForeignKey(
        'TMSAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'TicketStatus'
        verbose_name_plural = 'TicketStatus'


class TicketPriority(models.Model):

    name = models.CharField(max_length=2048)

    access_token = models.ForeignKey(
        'TMSAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'TicketPriority'
        verbose_name_plural = 'TicketPrioritys'


class TMSAccessToken(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique access token key')

    agent = models.OneToOneField('Agent', on_delete=models.CASCADE,
                                 unique=True, help_text='admin responsible for the same')

    ticket_statuses = models.ManyToManyField(
        'TicketStatus', blank=True)

    ticket_priorities = models.ManyToManyField(
        'TicketPriority', blank=True)

    tms_console_theme_color = models.CharField(
        null=True, blank=True, max_length=200, default=DEFAULT_TMS_CONSOLE_THEME_COLOR)

    tms_console_logo = models.CharField(
        max_length=500, null=True, blank=True, help_text='source of TMS console logo')

    cognoai_celebration = models.BooleanField(
        default=True, help_text="cognoai celebration is enabled or not")

    cognoai_quote = models.BooleanField(
        default=True, help_text="cognoai quotes is enabled or not")

    auth_token = models.CharField(max_length=100, null=True, blank=True,
                                  help_text='Authorization token for authentication [this will be auto generated]')

    def get_dark_theme_color(self):
        try:
            tms_console_theme_color = json.loads(
                self.tms_console_theme_color)
            return self.get_color_by_percent(tms_console_theme_color, -26)
        except Exception:
            return None

    def get_tms_console_theme_color(self):
        try:
            tms_console_theme_color = json.loads(
                self.tms_console_theme_color)
            return tms_console_theme_color
        except Exception:
            return None

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

    def get_whatsapp_api_processor_obj(self):
        try:
            assign_task_processor = WhatsappApiProcessor.objects.filter(
                access_token=self).first()
            if assign_task_processor == None:
                assign_task_processor = WhatsappApiProcessor.objects.create(
                    access_token=self)
            return assign_task_processor
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error get_assign_task_processor_obj %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            return None

    def __str__(self):
        return str(self.key) + " - " + str(self.agent.user.username)

    def name(self):
        return str(self.key) + " - " + str(self.agent.user.username)

    class Meta:
        verbose_name = 'TMSAccessToken'
        verbose_name_plural = 'TMSAccessToken'


@receiver(post_save, sender=TMSAccessToken)
def set_access_token_default_settings(sender, instance, created, *args, **kwargs):
    if (not kwargs["raw"]) and created:
        create_ticket_priority_obj("LOW", instance, TicketPriority)
        create_ticket_priority_obj("MEDIUM", instance, TicketPriority)
        create_ticket_priority_obj("HIGH", instance, TicketPriority)
        create_ticket_priority_obj("URGENT", instance, TicketPriority)
        create_ticket_status_obj("UNASSIGNED", instance, TicketStatus)
        create_ticket_status_obj("PENDING", instance, TicketStatus)
        create_ticket_status_obj("RESOLVED", instance, TicketStatus)


class AgentPasswordHistory(models.Model):

    agent = models.ForeignKey(Agent, null=True, blank=True,
                              on_delete=models.CASCADE, help_text='Agent')

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when password is saved')

    password_hash = models.TextField(help_text="password hash")

    def __str__(self):
        return self.agent.user.username

    class Meta:
        verbose_name = 'AgentPasswordHistory'
        verbose_name_plural = 'AgentPasswordHistory'


class UserNotification(models.Model):

    agent = models.ForeignKey(
        Agent, null=True, blank=True, on_delete=models.CASCADE, help_text="Notification for this agent")

    ticket = models.ForeignKey(
        Ticket, null=True, blank=True, on_delete=models.SET_NULL, help_text="Ticket for which notification is sending.")

    datetime = models.DateTimeField(default=timezone.now, help_text="Time when notification is generated.")

    description = models.TextField(null=True, blank=True, help_text="Notification Data")

    is_checked = models.BooleanField(
        default=False, help_text="Designates whether this notification checked by user or not.", db_index=True)

    def __str__(self):
        return str(self.ticket.ticket_id) + " - " + str(self.agent.user.username) + " - " + str(self.description)

    class Meta:
        verbose_name = 'UserNotification'
        verbose_name_plural = 'UserNotifications'


class ExportRequest(models.Model):

    email_id = models.CharField(
        max_length=500, null=False, blank=False, help_text='Email address to send report')

    export_type = models.CharField(
        max_length=256, null=True, blank=True, choices=EXPORT_CHOICES)

    start_date = models.DateTimeField(default=timezone.now)

    end_date = models.DateTimeField(default=timezone.now)

    agent = models.ForeignKey(
        'Agent', null=False, blank=False, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return self.agent.user.username + " - " + self.email_id + " - " + self.export_type + " - " + str(self.is_completed)

    class Meta:
        verbose_name = 'ExportRequest'
        verbose_name_plural = 'ExportRequests'


class FileAccessManagement(models.Model):

    key = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False, help_text='unique access token key')

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True,
        help_text="Original name of file without adding any marker to make it unique")

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.original_file_name)

    class Meta:
        verbose_name = 'FileAccessManagement'
        verbose_name_plural = 'FileAccessManagement'


class CRMIntegrationModel(models.Model):

    access_token = models.ForeignKey(
        'TMSAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    auth_token = models.CharField(max_length=100, null=True, blank=True, unique=True,
                                  help_text='Auto generated authorization token', db_index=True)

    datetime = models.DateTimeField(
        default=timezone.now, help_text='datetime when token was generated')

    is_expired = models.BooleanField(default=False)

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


class WhatsappApiProcessor(models.Model):

    access_token = models.OneToOneField(
        'TMSAccessToken', null=True, blank=False, on_delete=models.CASCADE)

    function = models.TextField(
        default=WHATSAPP_API_PROCESSOR_CODE, null=True, blank=True, help_text="Function code")

    class Meta:
        verbose_name = "WhatsappApiProcessor"
        verbose_name_plural = "WhatsappApiProcessor"

    def __str__(self):
        return self.access_token.agent.user.username


class WhatsappApiProcessorLogger(models.Model):

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, help_text='admin responsible for the same')

    function = models.TextField(
        null=True, blank=True, help_text="Function code")

    assign_task_process = models.ForeignKey(
        'WhatsappApiProcessor', null=True, blank=True, on_delete=models.CASCADE)

    datetime = models.DateTimeField(
        null=True, blank=True, default=timezone.now)

    def __str__(self):
        return str(self.datetime) + " - " + str(self.assign_task_process.access_token.key) + " - " + self.agent.user.username
