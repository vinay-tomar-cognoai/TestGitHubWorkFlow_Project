from django.db import models
from django.utils import timezone
from AuditTrailApp.constants import *
import uuid


class CognoAIAuditTrail(models.Model):
    app_name = models.TextField(null=False,
                                blank=False,
                                choices=APP_NAMES,
                                help_text="App Name")

    user = models.ForeignKey(
        "EasyChatApp.User", on_delete=models.CASCADE)

    datetime = models.DateTimeField(default=timezone.now)

    action_type = models.TextField(null=False,
                                   blank=False,
                                   choices=ACTION_TYPES,
                                   help_text="Performed Action")

    description = models.TextField(null=True, blank=True)

    request_data_dump = models.TextField(null=True, blank=True)

    api_end_point = models.TextField(null=True, blank=True)

    ip_address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.app_name + " - " + self.action_type

    class Meta:
        verbose_name = 'CognoAIAuditTrail'
        verbose_name_plural = 'CognoAIAuditTrail'


class ExportRequest(models.Model):

    email_id = models.CharField(
        max_length=500, null=False, blank=False, help_text='Email address to send report')

    export_type = models.CharField(
        max_length=256, null=True, blank=True, choices=EXPORT_CHOICES)

    start_date = models.DateTimeField(default=timezone.now)

    end_date = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return self.user.username + " - " + self.email_id

    class Meta:
        verbose_name = 'ExportRequest'
        verbose_name_plural = 'ExportRequests'


class FileAccessManagement(models.Model):

    key = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False, help_text='unique access token key')

    file_path = models.CharField(max_length=2000, null=False, blank=False)

    original_file_name = models.CharField(
        max_length=2000, null=True, blank=True, help_text="Original name of file without adding any marker to make it unique")

    def __str__(self):
        return str(self.key) + " - " + str(self.file_path) + " - " + str(self.original_file_name)

    class Meta:
        verbose_name = 'FileAccessManagement'
        verbose_name_plural = 'FileAccessManagement'
