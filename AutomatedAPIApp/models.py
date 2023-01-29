from django.db import models

# Create your models here.
from EasyChatApp.models import Tree, ApiTree


class AutomatedAPI(models.Model):

    request_type = models.CharField(
        max_length=10, null=False, blank=False, default="POST")

    request_url = models.CharField(
        max_length=500, null=False, blank=False, default="http://127.0.0.1:8000")

    headers = models.TextField(null=True, blank=True)

    authorization = models.TextField(null=True, blank=True)

    request_packet = models.TextField(null=True, blank=Tree)

    sample_response_packet = models.TextField(null=True, blank=True)

    variables = models.TextField(null=True, blank=True)

    next_api = models.ForeignKey(
        "AutomatedAPI", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'AutomatedAPI'


class AutomatedAPIIntegration(models.Model):

    initial_api = models.ForeignKey(
        AutomatedAPI, null=True, blank=True, on_delete=models.CASCADE)

    tree = models.ForeignKey("EasyChatApp.Tree", on_delete=models.CASCADE)

    api_tree = models.ForeignKey(
        "EasyChatApp.ApiTree", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'AutomatedAPIIntegration'
