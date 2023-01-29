from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
import json


class Tester(models.Model):

    user = models.OneToOneField(
        "EasyChatApp.User", on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Tester'

# method for updating


class BotQATesting(models.Model):

    bot_name = models.CharField(max_length=100, null=False, blank=False)

    bot_id = models.IntegerField(null=False, blank=False)

    bot_domain = models.CharField(max_length=1000, null=False, blank=False)

    created_by = models.ForeignKey(Tester, on_delete=models.CASCADE)

    created_at = models.DateTimeField(default=timezone.now)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.bot_name

    class Meta:
        verbose_name = 'BotQATesting'


class BotQATestCase(models.Model):

    bot = models.ForeignKey(BotQATesting, null=False,
                            blank=False, on_delete=models.CASCADE)

    uploaded_excel = models.CharField(max_length=1000, null=False, blank=False)

    secured_file_path = models.CharField(max_length=1000, null=True, blank=False)

    is_uploaded = models.BooleanField(default=False)

    parsed_json = models.TextField(null=True, blank=True)

    is_parsed = models.BooleanField(default=False)

    testing_start_datetime = models.DateTimeField(null=True, blank=True)

    is_tested = models.BooleanField(default=False)

    def __str__(self):
        return self.bot.bot_name

    def total_number_of_flows(self):
        return BotQATestCaseFlow.objects.filter(qa_testcase=self).count()

    def total_number_of_flows_tested(self):
        return BotQATestCaseFlow.objects.filter(qa_testcase=self, is_flow_tested=True).count()

    def total_number_of_flows_failed(self):
        return BotQATestCaseFlow.objects.filter(qa_testcase=self, is_flow_testing_failed=True).count()

    class Meta:
        verbose_name = 'BotQATestCase'


class BotQATestCaseFlow(models.Model):

    qa_testcase = models.ForeignKey(
        BotQATestCase, null=False, blank=False, on_delete=models.CASCADE)

    parsed_json = models.TextField(null=False, blank=False)

    is_flow_testing_failed = models.BooleanField(default=False)

    is_flow_tested = models.BooleanField(default=False)

    output_flow = models.TextField(null=True, blank=True)

    minimized_output_flow = models.TextField(null=True, blank=True)

    total_execution_time = models.CharField(
        max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.qa_testcase.pk) + " - " + self.qa_testcase.bot.bot_name

    def get_flow_name(self):
        try:
            return json.loads(self.parsed_json)["flow"]
        except Exception:
            return "Not available"

    def get_intent_pk(self):
        try:
            return json.loads(self.parsed_json)["intent_pk"]
        except Exception:
            return "Not available"

    def get_total_execution_time(self):
        try:
            return round(float(self.total_execution_time), 2)
        except Exception:
            return "Not available"

    class Meta:
        verbose_name = 'BotQATestCaseFlow'
