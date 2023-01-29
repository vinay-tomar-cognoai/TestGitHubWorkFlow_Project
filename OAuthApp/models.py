from django.db import models

from django.utils import timezone

# Create your models here.

import uuid

REMOTE_ACCESS_IP_ADDRESSES = ["65.2.65.107"]

REMOTE_ACCESS_URL = "https://remote-access.allincall.in"


class CentralizedAccessToken(models.Model):

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text='unique login token for centralized login')

    validation_token = models.CharField(
        max_length=200, null=False, blank=False)

    user_id = models.CharField(max_length=300, null=False, blank=False)

    datetime = models.DateTimeField(default=timezone.now)

    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.session_id)

    class Meta:
        verbose_name = "CentralizedAccessToken"
        verbose_name_plural = "CentralizedAccessTokens"
