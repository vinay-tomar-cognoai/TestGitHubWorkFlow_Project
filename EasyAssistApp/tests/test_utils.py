#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.encrypt import CustomEncrypt
from EasyAssistApp.utils import *
from requests.auth import HTTPBasicAuth
import hashlib
import logging
import time
import json
import random
import execjs
import base64
import os
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)


class Utils(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: views...', extra={
                    'AppName': 'EasyAssist'})
        user = User.objects.create(username='testeasyassist',
                                   password='testeasyassist')
        support_user = \
            User.objects.create(username='support_testeasyassist',
                                password='testeasyassist')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasyassist',
                                password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.create(user=user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_agent = CobrowseAgent.objects.create(user=support_user)
        cobrowse_agent.is_switch_allowed = False
        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_agent = \
            CobrowseAgent.objects.create(user=supervisor_user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'supervisor'
        cobrowse_agent.save()

    def tearDown(self):
        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token_obj in access_token_objs:
            delete_access_token_specific_static_file(str(access_token_obj.key))

    # def test_UrlShortenTinyurl(self):
    #     logger.info('Testing test_UrlShortenTinyurl...',
    #                 extra={'AppName': 'EasyAssist'})

    #     shorten_tiny_url_obj = UrlShortenTinyurl()
    #     generated_link = shorten_tiny_url_obj.shorten(
    #         "https://www.hdfccredila.com/apply-for-loan.html")

    #     generated_link_regex = r"https:[/][/]tinyurl.com[/]\S+"
    #     self.assertNotEqual(
    #         re.match(generated_link_regex, generated_link), None)

    def test_convert_seconds_to_hours_minutes(self):
        logger.info('Testing test_convert_seconds_to_hours_minutes...',
                    extra={'AppName': 'EasyAssist'})

        total_seconds = 45 + 45 * 60 + 1 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "1 hour 45 minutes")

        total_seconds = 0 + 45 * 60 + 1 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "1 hour 45 minutes")

        total_seconds = 45 + 25 * 60 + 2 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "2 hours 25 minutes")

        total_seconds = 0 + 0 * 60 + 2 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "2 hours")

        total_seconds = 45 + 0 * 60 + 1 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "1 hour")

        total_seconds = 0 + 0 * 60 + 2 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "2 hours")

        total_seconds = 0 + 0 * 60 + 0 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "0 minute")

        total_seconds = 0 + 1 * 60 + 0 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "1 minute")

        total_seconds = 0 + 2 * 60 + 0 * 60 * 60
        self.assertEqual(convert_seconds_to_hours_minutes(
            total_seconds), "2 minutes")

    def test_remo_html_from_string(self):
        logger.info('Testing test_remo_html_from_string...',
                    extra={'AppName': 'EasyAssist'})

        self.assertEqual(remo_html_from_string(
            "Hello there<html><p>p</p>okok"), "Hello therepokok")

        self.assertEqual(remo_html_from_string(
            " <<<<<<<<<<  <<<<<<<<, <<<<< <p> Hello there< html   >< p > p </ p >okok >>"), "  Hello there p okok >>")

    def test_remo_special_tag_from_string(self):
        logger.info('Testing test_remo_special_tag_from_string...',
                    extra={'AppName': 'EasyAssist'})

        input_string = "abc123ABC`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|abc123ABC"
        target_string = "abc123ABC`~!@#$%^&*()_\\]}[{'\";:/?.>,<`~!@#$%^&*()_\\]}[{'\";:/?.>,<`~!@#$%^&*()_\\]}[{'\";:/?.>,<abc123ABC"

        self.assertEqual(remo_special_tag_from_string(
            input_string), target_string)

    def test_remove_special_chars_from_filename(self):
        logger.info('Testing test_remove_special_chars_from_filename...',
                    extra={'AppName': 'EasyAssist'})

        input_string = "abc123ABC`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|`~!@#$%^&*()-_=+\\]}[{'\";:/?.>,<|abc123ABC"
        target_string = "abc123ABC`~!#$%^*()-_=+\\]}[{'\";:/?.,|`~!#$%^*()-_=+\\]}[{'\";:/?.,|`~!#$%^*()-_=+\\]}[{'\";:/?.,|abc123ABC"

        self.assertEqual(remove_special_chars_from_filename(
            input_string), target_string)

    def test_check_and_update_lead(self):
        logger.info('Testing test_check_and_update_lead...',
                    extra={'AppName': 'EasyAssist'})

        custom_encrypt_obj = CustomEncrypt()

        def get_md5_val(value):
            value = value.strip().lower()
            return hashlib.md5(value.encode()).hexdigest()

        # fresh cobrowse session and new primary value
        primary_value_list = [{"value": "9512395123", "label": "Phone"}, {
            "value": "test@gmail.com", "label": "Email"}]

        easyassist_sync_data = [{'value': '9512395123',
                                 'sync_type': 'primary',
                                 'name': 'Mobile Number', },
                                {'value': 'test@gmail.com',
                                 'sync_type': 'primary',
                                 'name': 'Email Id', }]

        meta_data = {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                         'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                         'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                         },
                     'easyassist_sync_data': easyassist_sync_data}

        meta_data = json.dumps(meta_data)
        meta_data = custom_encrypt_obj.encrypt(meta_data)

        cobrowse_io = CobrowseIO.objects.create()
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()
        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()
        cobrowse_io.access_token = access_token

        check_and_update_lead(primary_value_list, meta_data,
                              cobrowse_io, CobrowseCapturedLeadData)

        md5_value_list = [get_md5_val(value['value'])
                          for value in primary_value_list]
        lead_objs = list(CobrowseCapturedLeadData.objects.filter(
            primary_value__in=md5_value_list, session_id=str(cobrowse_io.session_id)))

        self.assertEqual(len(lead_objs), 2)

        cobrowse_io = CobrowseIO.objects.get(
            session_id=str(cobrowse_io.session_id))

        for lead_obj in lead_objs:
            self.assertIn(lead_obj, list(cobrowse_io.captured_lead.all()))
        self.assertEqual(cobrowse_io.meta_data, meta_data)

        # primary value update test
        primary_value_list = [{"value": "9512395123", "label": "Phone"}, {
            "value": "test@gmail.com", "label": "Email"}]

        easyassist_sync_data = [{'value': '9512395456',
                                 'sync_type': 'primary',
                                 'name': 'Mobile Number', },
                                {'value': 'test2@gmail.com',
                                 'sync_type': 'primary',
                                 'name': 'Email Id', }]

        meta_data = {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                         'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                         'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                         },
                     'easyassist_sync_data': easyassist_sync_data}

        meta_data = json.dumps(meta_data)
        meta_data = custom_encrypt_obj.encrypt(meta_data)

        check_and_update_lead(primary_value_list, meta_data,
                              cobrowse_io, CobrowseCapturedLeadData)

        def get_md5_val(value):
            value = value.strip().lower()
            return hashlib.md5(value.encode()).hexdigest()

        md5_value_list = [get_md5_val(value['value'])
                          for value in primary_value_list]

        lead_objs = list(CobrowseCapturedLeadData.objects.filter(
            primary_value__in=md5_value_list, session_id=str(cobrowse_io.session_id)))

        self.assertEqual(len(lead_objs), 2)

        cobrowse_io = CobrowseIO.objects.get(
            session_id=str(cobrowse_io.session_id))

        for lead_obj in lead_objs:
            self.assertIn(lead_obj, list(cobrowse_io.captured_lead.all()))
        self.assertEqual(cobrowse_io.meta_data, meta_data)

    def test_add_supported_language(self):
        logger.info('Testing test_add_supported_language...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        supported_language_list = []

        supported_language_list.append(
            LanguageSupport.objects.create(title="Hindi").pk)
        supported_language_list.append(
            LanguageSupport.objects.create(title="Gujarati").pk)
        supported_language_list.append(
            LanguageSupport.objects.create(title="Marathi").pk)
        supported_language_list.append(
            LanguageSupport.objects.create(title="English").pk)

        add_supported_language(
            cobrowse_agent, supported_language_list, LanguageSupport)

        for supported_language in supported_language_list:
            supported_language = LanguageSupport.objects.get(
                pk=supported_language)
            self.assertIn(supported_language, list(
                cobrowse_agent.supported_language.all()))

    def test_add_supported_product(self):
        logger.info('Testing test_add_supported_product...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        supported_product_list = []

        supported_product_list.append(
            ProductCategory.objects.create(title="Car Loan").pk)
        supported_product_list.append(
            ProductCategory.objects.create(title="Home Loan").pk)

        add_supported_product(
            cobrowse_agent, supported_product_list, ProductCategory)

        for supported_product in supported_product_list:
            supported_product = ProductCategory.objects.get(
                pk=supported_product)
            self.assertIn(supported_product, list(
                cobrowse_agent.product_category.all()))

    def test_add_selected_supervisor(self):
        logger.info('Testing test_add_selected_supervisor...',
                    extra={'AppName': 'EasyAssist'})

        active_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username="support_testeasyassist")

        supervisor_testeasyassist = \
            CobrowseAgent.objects.get(
                user__username="supervisor_testeasyassist")

        selected_supervisor_pk_list = ['-1', supervisor_testeasyassist.pk]

        add_selected_supervisor(
            selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)

        self.assertIn(cobrowse_agent, list(active_agent.agents.all()))
        self.assertIn(cobrowse_agent, list(
            supervisor_testeasyassist.agents.all()))

    def test_reset_agents_language(self):
        logger.info('Testing test_reset_agents_language...',
                    extra={'AppName': 'EasyAssist'})

        exclude_agent_list = [
            'testeasyassist', 'support_testeasyassist', 'supervisor_testeasyassist']

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin')

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor')

        supervisor2_user = User.objects.create(
            username='supervisor2', password='supervisor2supervisor2')
        supervisor2_agent = CobrowseAgent.objects.create(
            user=supervisor2_user, role='supervisor')

        agent1_user = User.objects.create(
            username='agent1', password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(
            user=agent1_user, role='agent')

        agent2_user = User.objects.create(
            username='agent2', password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(
            user=agent2_user, role='agent')

        agent3_user = User.objects.create(
            username='agent3', password='agent3agent3')
        agent3_agent = CobrowseAgent.objects.create(
            user=agent3_user, role='agent')

        agent4_user = User.objects.create(
            username='agent4', password='agent4agent4')
        agent4_agent = CobrowseAgent.objects.create(
            user=agent4_user, role='agent')

        agent5_user = User.objects.create(
            username='agent5', password='agent5agent5')
        agent5_agent = CobrowseAgent.objects.create(
            user=agent5_user, role='agent')

        agent6_user = User.objects.create(
            username='agent6', password='agent6agent6')
        agent6_agent = CobrowseAgent.objects.create(
            user=agent6_user, role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(supervisor2_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.agents.add(agent4_agent)
        admin_agent.save()
        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.agents.add(agent3_agent)
        supervisor1_agent.agents.add(agent5_agent)
        supervisor1_agent.save()
        supervisor2_agent.agents.add(agent6_agent)
        supervisor2_agent.save()

        supported_language1 = LanguageSupport.objects.filter(
            title="English").first()
        supported_language2 = LanguageSupport.objects.create(title="Hindi")

        agent_objs = CobrowseAgent.objects.filter(
            ~Q(user__username__in=exclude_agent_list))

        for agent_obj in agent_objs:
            agent_obj.supported_language.add(supported_language1)
            agent_obj.save()

        agent_objs = agent_objs.exclude(user=supervisor2_agent.user)

        for agent_obj in agent_objs:
            agent_obj.supported_language.add(supported_language2)
            agent_obj.save()

        agent_objs = CobrowseAgent.objects.filter(
            ~Q(user__username__in=exclude_agent_list))

        for agent_obj in agent_objs:
            self.assertIn(supported_language1, list(
                agent_obj.supported_language.all()))
            if agent_obj == supervisor2_agent:
                self.assertNotIn(supported_language2, list(
                    agent_obj.supported_language.all()))
            else:
                self.assertIn(supported_language2, list(
                    agent_obj.supported_language.all()))

        admin_agent.supported_language.remove(supported_language2)
        admin_agent.save()
        reset_agents_language(admin_agent)

        for agent_obj in agent_objs:
            self.assertIn(supported_language1, list(
                agent_obj.supported_language.all()))
            self.assertNotIn(supported_language2, list(
                agent_obj.supported_language.all()))

    def test_archive_meeting_objects(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)
        meeting_start_datetime = datetime.now() - timedelta(days=1)
        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=meeting_start_datetime.date(),
            meeting_start_time=meeting_start_datetime.time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_expired=False)
        meeting_id = meeting_io.meeting_id

        archive_meeting_objects(CobrowseVideoConferencing)

        meeting_io = CobrowseVideoConferencing.objects.filter(
            meeting_id=meeting_id).first()
        self.assertEqual(meeting_io.is_expired, True)

        meeting_end_datetime = datetime.now() - timedelta(minutes=5)
        meeting_start_datetime = datetime.now() - timedelta(minutes=50)
        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=meeting_start_datetime.date(),
            meeting_start_time=meeting_start_datetime.time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_expired=False)
        meeting_id = meeting_io.meeting_id

        archive_meeting_objects(CobrowseVideoConferencing)

        meeting_io = CobrowseVideoConferencing.objects.filter(
            meeting_id=meeting_id).first()
        self.assertEqual(meeting_io.is_expired, True)

        meeting_end_datetime = datetime.now() + timedelta(minutes=5)
        meeting_start_datetime = datetime.now() - timedelta(minutes=50)
        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=meeting_start_datetime.date(),
            meeting_start_time=meeting_start_datetime.time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_expired=False)
        meeting_id = meeting_io.meeting_id

        archive_meeting_objects(CobrowseVideoConferencing)

        meeting_io = CobrowseVideoConferencing.objects.filter(
            meeting_id=meeting_id).first()
        self.assertEqual(meeting_io.is_expired, False)

    def test_mask_cogno_meet_customer_details(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_expired=True)

        audit_trail_obj = CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        mobile_number = "9191919191"
        email_id = "test@example.com"
        chat_history = [
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "agent",
                "time": "07:40",
            }),
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "client",
                "time": "07:42",
            }),
            json.dumps({
                "type": "attachment",
                "message": mobile_number,
                "sender": "agent",
                "time": "07:44",
            }),
            json.dumps({
                "type": "attachment",
                "message": email_id,
                "sender": "client",
                "time": "07:46",
            }),
        ]

        audit_trail_obj.message_history = chat_history
        audit_trail_obj.save()
        mask_cogno_meet_customer_details(CobrowseVideoAuditTrail)

        audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(
            cobrowse_video=meeting_io).first()
        message_history = eval(audit_trail_obj.message_history)

        message = json.loads(message_history[2])
        hash_mobile = hashlib.sha256(mobile_number.encode()).hexdigest()
        self.assertEqual(hash_mobile, message["message"])

        message = json.loads(message_history[3])
        hash_email = hashlib.sha256(email_id.encode()).hexdigest()
        self.assertEqual(hash_email, message["message"])

    def test_update_resend_password_counter(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        for send_passowrd_request_counter in range(RESEND_PASSWORD_THRESHOLD):
            update_resend_password_counter(cobrowse_agent)
            self.assertEqual(
                cobrowse_agent.last_password_resend_date, timezone.now().date())
            self.assertEqual(cobrowse_agent.resend_password_count,
                             RESEND_PASSWORD_THRESHOLD - send_passowrd_request_counter - 1)

    def test_analytics_ongoing_meeting_count(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
            agent=cobrowse_agent)
        total_ongoing_meeting = analytics_ongoing_meeting_count(
            cogno_vid_objs, CobrowseVideoAuditTrail)
        self.assertEqual(total_ongoing_meeting, 1)

    def test_calculate_agent_online_and_work_time(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(datetime.now() - timedelta(hours=2)),
            last_online_end_datetime=datetime.now())

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() - timedelta(hours=1)),
            session_end_datetime=datetime.now())

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() + timedelta(minutes=20)),
            session_end_datetime=datetime.now() + timedelta(minutes=40))

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(datetime.now() + timedelta(hours=2)),
            last_online_end_datetime=datetime.now() + timedelta(hours=4))

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() + timedelta(hours=3)),
            session_end_datetime=datetime.now() + timedelta(hours=5))

        work_audit_trail_objs = CobrowseAgentWorkAuditTrail.objects.filter(
            agent=cobrowse_agent)
        online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent=cobrowse_agent)
        total_time = calculate_agent_online_and_work_time(
            online_audit_trail_objs, work_audit_trail_objs)
        self.assertEqual(total_time, 7199)

    def test_calcuate_agent_online_session_common_time(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(datetime.now() - timedelta(hours=2)),
            last_online_end_datetime=datetime.now())

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() - timedelta(hours=1)),
            session_end_datetime=datetime.now())

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() + timedelta(minutes=20)),
            session_end_datetime=datetime.now() + timedelta(minutes=40))

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(datetime.now() + timedelta(hours=2)),
            last_online_end_datetime=datetime.now() + timedelta(hours=4))

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() + timedelta(hours=3)),
            session_end_datetime=datetime.now() + timedelta(hours=5))

        work_audit_trail_objs = CobrowseAgentWorkAuditTrail.objects.filter(
            agent=cobrowse_agent)
        online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent=cobrowse_agent)

        common_time_list = []
        for online_audit_trail_obj in online_audit_trail_objs:
            common_time_list.append([
                online_audit_trail_obj.last_online_start_datetime,
                online_audit_trail_obj.last_online_end_datetime,
                "online"
            ])

        for work_audit_trail_obj in work_audit_trail_objs:
            common_time_list.append([
                work_audit_trail_obj.session_start_datetime,
                work_audit_trail_obj.session_end_datetime,
                "work"
            ])

        total_time = calcuate_agent_online_session_common_time(
            common_time_list)
        self.assertEqual(total_time, 7199)

    def test_get_common_online_and_work_time(self):
        past_interval_start_time = datetime.now() - timedelta(hours=2)
        past_interval_end_time = datetime.now() - timedelta(hours=1)
        active_interval_start_time = datetime.now() - timedelta(minutes=40)
        active_interval_end_time = datetime.now()
        total_time = get_common_online_and_work_time(
            past_interval_start_time, past_interval_end_time, active_interval_start_time, active_interval_end_time)
        self.assertEqual(total_time, 0)

        active_interval_start_time = datetime.now() - timedelta(hours=2)
        active_interval_end_time = datetime.now() - timedelta(hours=1)
        past_interval_start_time = datetime.now() - timedelta(minutes=40)
        past_interval_end_time = datetime.now()
        total_time = get_common_online_and_work_time(
            past_interval_start_time, past_interval_end_time, active_interval_start_time, active_interval_end_time)
        self.assertNotEqual(total_time, 0)

        past_interval_start_time = datetime.now() - timedelta(hours=2)
        active_interval_start_time = datetime.now() - timedelta(hours=1)
        active_interval_end_time = datetime.now() - timedelta(minutes=40)
        past_interval_end_time = datetime.now()
        total_time = get_common_online_and_work_time(
            past_interval_start_time, past_interval_end_time, active_interval_start_time, active_interval_end_time)
        self.assertEqual(int(total_time), 1200)

    def test_calculate_agent_cobrowsing_meeting_session_duration(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() - timedelta(hours=2)),
            session_end_datetime=datetime.now())

        work_audit_trail_objs = CobrowseAgentWorkAuditTrail.objects.filter(
            agent=cobrowse_agent)
        work_duration = calculate_agent_cobrowsing_meeting_session_duration(
            work_audit_trail_objs)
        self.assertEqual(work_duration, 7200)

        CobrowseAgentWorkAuditTrail.objects.create(
            agent=cobrowse_agent,
            session_start_datetime=(datetime.now() + timedelta(minutes=20)),
            session_end_datetime=datetime.now() + timedelta(minutes=30))

        work_audit_trail_objs = CobrowseAgentWorkAuditTrail.objects.filter(
            agent=cobrowse_agent)
        work_duration = calculate_agent_cobrowsing_meeting_session_duration(
            work_audit_trail_objs)
        self.assertEqual(work_duration, 7800)

    def test_calculate_agent_online_duration(self):
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(datetime.now() - timedelta(hours=2)),
            last_online_end_datetime=datetime.now())

        online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent=cobrowse_agent)
        total_online_duration = calculate_agent_online_duration(
            online_audit_trail_objs)
        self.assertEqual(total_online_duration, 7200)

        CobrowseAgentOnlineAuditTrail.objects.create(
            agent=cobrowse_agent,
            last_online_start_datetime=(
                datetime.now() + timedelta(minutes=20)),
            last_online_end_datetime=datetime.now() + timedelta(minutes=30))

        online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent=cobrowse_agent)
        total_online_duration = calculate_agent_online_duration(
            online_audit_trail_objs)
        self.assertEqual(total_online_duration, 7800)

    def test_get_online_duration_within_agent_login_session(self):
        login_datetime = datetime.now() - timedelta(hours=2)
        logout_datetime = datetime.now()
        online_start_datetime = datetime.now() - timedelta(hours=1)
        online_end_datetime = datetime.now() - timedelta(minutes=20)
        total_time = get_online_duration_within_agent_login_session(
            login_datetime, logout_datetime, online_start_datetime, online_end_datetime)
        self.assertEqual(total_time, 2400)

        login_datetime = datetime.now() - timedelta(hours=3)
        logout_datetime = datetime.now() - timedelta(hours=1)
        online_start_datetime = datetime.now() - timedelta(hours=2)
        online_end_datetime = datetime.now()
        total_time = get_online_duration_within_agent_login_session(
            login_datetime, logout_datetime, online_start_datetime, online_end_datetime)
        self.assertEqual(total_time, 3599)

        login_datetime = datetime.now() - timedelta(hours=1)
        logout_datetime = datetime.now()
        online_start_datetime = datetime.now() - timedelta(hours=2)
        online_end_datetime = datetime.now()
        total_time = get_online_duration_within_agent_login_session(
            login_datetime, logout_datetime, online_start_datetime, online_end_datetime)
        self.assertEqual(total_time, 3600)

        login_datetime = datetime.now() - timedelta(hours=2)
        logout_datetime = datetime.now() - timedelta(hours=1)
        online_start_datetime = datetime.now() - timedelta(hours=3)
        online_end_datetime = datetime.now()
        total_time = get_online_duration_within_agent_login_session(
            login_datetime, logout_datetime, online_start_datetime, online_end_datetime)
        self.assertEqual(total_time, 3600)

    def test_get_session_duration_within_agent_login_session(self):
        login_datetime = datetime.now() - timedelta(hours=2)
        logout_datetime = datetime.now()
        session_start_datetime = datetime.now() - timedelta(hours=1)
        session_end_datetime = datetime.now() - timedelta(minutes=20)
        total_time = get_session_duration_within_agent_login_session(
            login_datetime, logout_datetime, session_start_datetime, session_end_datetime)
        self.assertEqual(total_time, 2400)

        login_datetime = datetime.now() - timedelta(hours=3)
        logout_datetime = datetime.now() - timedelta(hours=1)
        session_start_datetime = datetime.now() - timedelta(hours=2)
        session_end_datetime = datetime.now()
        total_time = get_session_duration_within_agent_login_session(
            login_datetime, logout_datetime, session_start_datetime, session_end_datetime)
        self.assertEqual(total_time, 3599)

        login_datetime = datetime.now() - timedelta(hours=1)
        logout_datetime = datetime.now()
        session_start_datetime = datetime.now() - timedelta(hours=2)
        session_end_datetime = datetime.now()
        total_time = get_session_duration_within_agent_login_session(
            login_datetime, logout_datetime, session_start_datetime, session_end_datetime)
        self.assertEqual(total_time, 3600)

        login_datetime = datetime.now() - timedelta(hours=2)
        logout_datetime = datetime.now() - timedelta(hours=1)
        session_start_datetime = datetime.now() - timedelta(hours=3)
        session_end_datetime = datetime.now()
        total_time = get_session_duration_within_agent_login_session(
            login_datetime, logout_datetime, session_start_datetime, session_end_datetime)
        self.assertEqual(total_time, 3600)

    def test_get_time_duration_with_login_session(self):
        login_time = datetime.now() - timedelta(hours=2)
        logout_time = datetime.now()
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now() - timedelta(minutes=20)

        start_datetime, end_datetime = get_time_duration_with_login_session(
            login_time, logout_time, start_time, end_time)
        self.assertEqual(start_datetime, start_time)
        self.assertEqual(end_datetime, end_time)

        login_time = datetime.now() - timedelta(hours=3)
        logout_time = datetime.now() - timedelta(hours=1)
        start_time = datetime.now() - timedelta(hours=2)
        end_time = datetime.now()

        start_datetime, end_datetime = get_time_duration_with_login_session(
            login_time, logout_time, start_time, end_time)
        self.assertEqual(start_datetime, start_time)
        self.assertEqual(end_datetime, logout_time)

        login_time = datetime.now() - timedelta(hours=1)
        logout_time = datetime.now()
        start_time = datetime.now() - timedelta(hours=2)
        end_time = datetime.now()

        start_datetime, end_datetime = get_time_duration_with_login_session(
            login_time, logout_time, start_time, end_time)
        self.assertEqual(start_datetime, login_time)
        self.assertEqual(end_datetime, logout_time)

        login_time = datetime.now() - timedelta(hours=2)
        logout_time = datetime.now() - timedelta(hours=1)
        start_time = datetime.now() - timedelta(hours=3)
        end_time = datetime.now()

        start_datetime, end_datetime = get_time_duration_with_login_session(
            login_time, logout_time, start_time, end_time)
        self.assertEqual(start_datetime, login_time)
        self.assertEqual(end_datetime, logout_time)

    def test_save_language_support(self):
        logger.info('Testing test_save_language_support...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        save_language_support(
            cobrowse_agent, "Gujarati, marathi, x", LanguageSupport)

        lang1 = LanguageSupport.objects.get(title="Gujarati")
        lang2 = LanguageSupport.objects.get(title="Marathi")

        self.assertEqual(cobrowse_agent.supported_language.all().count(), 3)
        self.assertIn(lang1, list(cobrowse_agent.supported_language.all()))
        self.assertIn(lang2, list(cobrowse_agent.supported_language.all()))

    def test_save_product_category(self):
        logger.info('Testing test_save_product_category...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        save_product_category(
            cobrowse_agent, "car loan, loan2, x", ProductCategory)

        prod1 = ProductCategory.objects.get(title="Car loan")
        prod2 = ProductCategory.objects.get(title="Loan2")

        self.assertEqual(cobrowse_agent.product_category.all().count(), 2)
        self.assertIn(prod1, list(cobrowse_agent.product_category.all()))
        self.assertIn(prod2, list(cobrowse_agent.product_category.all()))

    def test_reset_agents_product_category(self):
        logger.info('Testing test_reset_agents_product_category...',
                    extra={'AppName': 'EasyAssist'})

        exclude_agent_list = [
            'testeasyassist', 'support_testeasyassist', 'supervisor_testeasyassist']

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin')

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor')

        supervisor2_user = User.objects.create(
            username='supervisor2', password='supervisor2supervisor2')
        supervisor2_agent = CobrowseAgent.objects.create(
            user=supervisor2_user, role='supervisor')

        agent1_user = User.objects.create(
            username='agent1', password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(
            user=agent1_user, role='agent')

        agent2_user = User.objects.create(
            username='agent2', password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(
            user=agent2_user, role='agent')

        agent3_user = User.objects.create(
            username='agent3', password='agent3agent3')
        agent3_agent = CobrowseAgent.objects.create(
            user=agent3_user, role='agent')

        agent4_user = User.objects.create(
            username='agent4', password='agent4agent4')
        agent4_agent = CobrowseAgent.objects.create(
            user=agent4_user, role='agent')

        agent5_user = User.objects.create(
            username='agent5', password='agent5agent5')
        agent5_agent = CobrowseAgent.objects.create(
            user=agent5_user, role='agent')

        agent6_user = User.objects.create(
            username='agent6', password='agent6agent6')
        agent6_agent = CobrowseAgent.objects.create(
            user=agent6_user, role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(supervisor2_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.agents.add(agent4_agent)
        admin_agent.save()
        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.agents.add(agent3_agent)
        supervisor1_agent.agents.add(agent5_agent)
        supervisor1_agent.save()
        supervisor2_agent.agents.add(agent6_agent)
        supervisor2_agent.save()

        product_category1 = ProductCategory.objects.create(title="CarLoan")
        product_category2 = ProductCategory.objects.create(title="HomeLoan")

        agent_objs = CobrowseAgent.objects.filter(
            ~Q(user__username__in=exclude_agent_list))

        for agent_obj in agent_objs:
            agent_obj.product_category.add(product_category1)
            agent_obj.save()

        agent_objs = agent_objs.exclude(user=supervisor2_agent.user)

        for agent_obj in agent_objs:
            agent_obj.product_category.add(product_category2)
            agent_obj.save()

        agent_objs = CobrowseAgent.objects.filter(
            ~Q(user__username__in=exclude_agent_list))

        for agent_obj in agent_objs:
            self.assertIn(product_category1, list(
                agent_obj.product_category.all()))
            if agent_obj == supervisor2_agent:
                self.assertNotIn(product_category2, list(
                    agent_obj.product_category.all()))
            else:
                self.assertIn(product_category2, list(
                    agent_obj.product_category.all()))

        admin_agent.product_category.remove(product_category2)
        admin_agent.save()
        reset_agents_product_category(admin_agent)

        for agent_obj in agent_objs:
            self.assertIn(product_category1, list(
                agent_obj.product_category.all()))
            self.assertNotIn(product_category2, list(
                agent_obj.product_category.all()))

    def test_add_product_category_to_user(self):
        logger.info('Testing test_add_product_category_to_user...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        prod1 = ProductCategory.objects.create(title="CarLoan")
        prod2 = ProductCategory.objects.create(title="HomeLoan")

        selected_product_category_pk_list = [prod1.pk, prod2.pk]

        add_product_category_to_user(
            cobrowse_agent, selected_product_category_pk_list, ProductCategory)

        self.assertEqual(cobrowse_agent.product_category.all().count(), 2)
        self.assertIn(prod1, list(cobrowse_agent.product_category.all()))
        self.assertIn(prod2, list(cobrowse_agent.product_category.all()))

    def test_get_file_type(self):
        logger.info('Testing test_get_file_type...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        prod1 = ProductCategory.objects.create(title="CarLoan")
        prod2 = ProductCategory.objects.create(title="HomeLoan")

        selected_product_category_pk_list = [prod1.pk, prod2.pk]

        add_product_category_to_user(
            cobrowse_agent, selected_product_category_pk_list, ProductCategory)

        self.assertEqual(cobrowse_agent.product_category.all().count(), 2)
        self.assertIn(prod1, list(cobrowse_agent.product_category.all()))
        self.assertIn(prod2, list(cobrowse_agent.product_category.all()))

    def test_get_hashed_data(self):
        message = "abcpa123a"
        hash_pan = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_pan)

        message = "9292929292"
        hash_mobile = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_mobile)

        message = "9292929292123"
        hash_account = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_account)

        message = "10"
        hash_age = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_age)

        message = "10040"
        hash_house = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_house)

        message = "100a40Aadsf"
        hash_house = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_house)

        message = "2020-01-02"
        hash_house = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(get_hashed_data(message), hash_house)

        message = "customer"
        self.assertEqual(get_hashed_data(message), message)

    def test_hash_crucial_info_in_data(self):
        message = "Pan number is abcpa123a"
        hash_pan = hashlib.sha256("abcpa123a".encode()).hexdigest()
        hash_message = "Pan number is " + hash_pan
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "abcpa123a"
        hash_pan = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_pan)

        message = "Mobile number is 9292929292"
        hash_mobile = hashlib.sha256("9292929292".encode()).hexdigest()
        hash_message = "Mobile number is " + hash_mobile
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "9292929292"
        hash_mobile = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_mobile)

        message = "Account number is 9292929292123"
        hash_account = hashlib.sha256("9292929292123".encode()).hexdigest()
        hash_message = "Account number is " + hash_account
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "9292929292123"
        hash_account = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_account)

        message = "Age is 10"
        hash_age = hashlib.sha256("10".encode()).hexdigest()
        hash_message = "Age is " + hash_age
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "10"
        hash_age = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_age)

        message = "House number is 10040"
        hash_house = hashlib.sha256("10040".encode()).hexdigest()
        hash_message = "House number is " + hash_house
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "10040"
        hash_house = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_house)

        message = "Customer ID is 100a40Aadsf"
        hash_house = hashlib.sha256("100a40Aadsf".encode()).hexdigest()
        hash_message = "Customer ID is " + hash_house
        self.assertEqual(hash_crucial_info_in_data(message), hash_message)

        message = "100a40Aadsf"
        hash_house = hashlib.sha256(message.encode()).hexdigest()
        self.assertEqual(hash_crucial_info_in_data(message), hash_house)

        message = "My name is Test Customer"
        self.assertEqual(hash_crucial_info_in_data(message), message)

    def test_get_masked_data_if_hashed(self):
        message = "hello"
        self.assertEqual(get_masked_data_if_hashed(message), message)

        message = "hello world, this is great"
        self.assertEqual(get_masked_data_if_hashed(message), message)

        message = "hello"
        hash_message = hashlib.sha256(message.encode()).hexdigest()
        masked_message = hash_message[0:5] + "***" + hash_message[-2:]
        self.assertEqual(get_masked_data_if_hashed(
            hash_message), masked_message)

    def test_mask_hashed_data(self):
        message = "abcdefghijklmnop"
        masked_message = "abcde***op"
        self.assertEqual(mask_hashed_data(message), masked_message)

        hash_message = hashlib.sha256(message.encode()).hexdigest()
        masked_message = hash_message[0:5] + "***" + hash_message[-2:]
        self.assertEqual(mask_hashed_data(hash_message), masked_message)

    def test_get_cobrowse_access_token_obj(self):
        logger.info('Testing test_get_cobrowse_access_token_obj...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        response = client.get("https://www.hdfccredila.com")
        request = response.wsgi_request

        self.assertEqual(get_cobrowse_access_token_obj(
            request, CobrowseAccessToken), access_token)

    def test_get_active_agent_obj(self):
        logger.info('Testing test_get_active_agent_obj...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        client = APIClient()
        client.login(username='testeasyassist', password='testeasyassist')

        response = client.get("https://www.hdfccredila.com")
        request = response.wsgi_request

        self.assertEqual(get_active_agent_obj(
            request, CobrowseAgent), cobrowse_agent)

    def test_get_request_origin(self):
        logger.info('Testing test_get_request_origin...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com')

        client.login(username='testeasyassist', password='testeasyassist')

        response = client.get("https://www.hdfccredila.com")
        request = response.wsgi_request

        self.assertEqual(get_request_origin(request), "www.hdfccredila.com")

    def test_get_list_agents_under_admin(self):
        logger.info('Testing test_get_list_agents_under_admin...',
                    extra={'AppName': 'EasyAssist'})

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin', is_switch_allowed=True)

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor', is_switch_allowed=True)

        supervisor2_user = User.objects.create(
            username='supervisor2', password='supervisor2supervisor2')
        supervisor2_agent = CobrowseAgent.objects.create(
            user=supervisor2_user, role='supervisor', is_switch_allowed=True)

        agent1_user = User.objects.create(
            username='agent1', password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(
            user=agent1_user, role='agent')

        agent2_user = User.objects.create(
            username='agent2', password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(
            user=agent2_user, role='agent')

        agent3_user = User.objects.create(
            username='agent3', password='agent3agent3')
        agent3_agent = CobrowseAgent.objects.create(
            user=agent3_user, role='agent')

        agent4_user = User.objects.create(
            username='agent4', password='agent4agent4')
        agent4_agent = CobrowseAgent.objects.create(
            user=agent4_user, role='agent')

        agent5_user = User.objects.create(
            username='agent5', password='agent5agent5')
        agent5_agent = CobrowseAgent.objects.create(
            user=agent5_user, role='agent')

        agent6_user = User.objects.create(
            username='agent6', password='agent6agent6')
        agent6_agent = CobrowseAgent.objects.create(
            user=agent6_user, role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(supervisor2_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.agents.add(agent4_agent)
        admin_agent.save()
        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.agents.add(agent3_agent)
        supervisor1_agent.agents.add(agent5_agent)
        supervisor1_agent.save()
        supervisor2_agent.agents.add(agent6_agent)
        supervisor2_agent.save()

        '''

        admin_agent     supervisor1_agent       agent2_agent(b)
                                                agent3_agent
                                                agent5_agent

                        supervisor2_agent(b)    agent6_agent

                        agent1_agent
                        agent4_agent(b)

        '''

        self.assertEqual(
            len(get_list_agents_under_admin(admin_agent, None, None)), 9)

        agents = [agent2_agent, supervisor2_agent, agent4_agent]

        for agent in agents:
            agent.is_account_active = False
            agent.save()

        self.assertEqual(
            len(get_list_agents_under_admin(admin_agent, None, None)), 9)
        self.assertEqual(
            len(get_list_agents_under_admin(admin_agent, None)), 5)

        agents = [admin_agent, supervisor1_agent, agent2_agent, agent3_agent,
                  supervisor2_agent, agent6_agent, agent1_agent, agent4_agent]

        for agent in agents:
            agent.is_active = True
            agent.save()

        self.assertEqual(
            len(get_list_agents_under_admin(admin_agent, True)), 4)

        supervisor1_agent.is_switch_allowed = False
        supervisor1_agent.save()
        supervisor2_agent.is_switch_allowed = False
        supervisor2_agent.save()

        self.assertEqual(
            len(get_list_agents_under_admin(admin_agent, True)), 3)

    def test_get_list_supervisor_under_admin(self):
        logger.info('Testing test_get_list_supervisor_under_admin...',
                    extra={'AppName': 'EasyAssist'})

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin', is_switch_allowed=True)

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor')

        supervisor2_user = User.objects.create(
            username='supervisor2', password='supervisor2supervisor2')
        supervisor2_agent = CobrowseAgent.objects.create(
            user=supervisor2_user, role='supervisor', is_switch_allowed=True)

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(supervisor2_agent)
        admin_agent.save()

        self.assertEqual(
            len(get_list_supervisor_under_admin(admin_agent, None)), 2)

        supervisor1_agent.role = "agent"
        supervisor1_agent.save()
        supervisor2_agent.role = "agent"
        supervisor2_agent.save()

        self.assertEqual(
            len(get_list_supervisor_under_admin(admin_agent, None)), 0)

        supervisor1_agent.role = "supervisor"
        supervisor1_agent.is_active = True
        supervisor1_agent.save()
        supervisor2_agent.role = "supervisor"
        supervisor2_agent.is_active = True
        supervisor2_agent.save()

        self.assertEqual(
            len(get_list_supervisor_under_admin(admin_agent, True)), 2)

        supervisor2_agent.is_account_active = False
        supervisor2_agent.save()

        self.assertEqual(
            len(get_list_supervisor_under_admin(admin_agent, True)), 1)

    def test_get_admin_from_active_agent(self):
        logger.info('Testing test_get_admin_from_active_agent...',
                    extra={'AppName': 'EasyAssist'})

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin', is_switch_allowed=True)

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor')

        agent1_user = User.objects.create(
            username='agent1', password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(
            user=agent1_user, role='agent')

        agent2_user = User.objects.create(
            username='agent2', password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(
            user=agent2_user, role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.save()

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.save()
        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.save()

        self.assertEqual(get_admin_from_active_agent(
            agent1_agent, CobrowseAgent), admin_agent)
        self.assertEqual(get_admin_from_active_agent(
            agent2_agent, CobrowseAgent), admin_agent)
        self.assertEqual(get_admin_from_active_agent(
            supervisor1_agent, CobrowseAgent), admin_agent)

    def test_get_supervisor_from_active_agent(self):
        logger.info('Testing test_get_supervisor_from_active_agent...',
                    extra={'AppName': 'EasyAssist'})

        admin_user = User.objects.create(
            username='admin', password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(
            user=admin_user, role='admin', is_switch_allowed=True)

        supervisor1_user = User.objects.create(
            username='supervisor1', password='supervisor1supervisor1')
        supervisor1_agent = CobrowseAgent.objects.create(
            user=supervisor1_user, role='supervisor', is_switch_allowed=True)

        agent1_user = User.objects.create(
            username='agent1', password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(
            user=agent1_user, role='agent')

        agent2_user = User.objects.create(
            username='agent2', password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(
            user=agent2_user, role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.save()

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.save()

        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.save()

        self.assertEqual(get_supervisor_from_active_agent(
            agent1_agent, CobrowseAgent), [admin_agent])
        self.assertEqual(get_supervisor_from_active_agent(
            agent2_agent, CobrowseAgent), [supervisor1_agent])

        client = APIClient()
        client.login(username='admin',
                     password='adminadmin')
        json_string = json.dumps({'active_status': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/switch-agent-mode/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()

        self.assertEqual(get_supervisor_from_active_agent(
            admin_agent, CobrowseAgent), [admin_agent])

        client = APIClient()
        client.login(username='supervisor1',
                     password='supervisor1supervisor1')
        json_string = json.dumps({'active_status': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/switch-agent-mode/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()

        self.assertEqual(get_supervisor_from_active_agent(
            supervisor1_agent, CobrowseAgent), [admin_agent, supervisor1_agent])
        self.assertEqual(get_supervisor_from_active_agent(
            agent1_agent, CobrowseAgent), [admin_agent])
        self.assertEqual(get_supervisor_from_active_agent(
            agent2_agent, CobrowseAgent), [supervisor1_agent])

    def test_save_audit_trail(self):
        logger.info('Testing test_save_audit_trail...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        save_audit_trail(cobrowse_agent, "1", "description",
                         CobrowsingAuditTrail)

        self.assertEqual(CobrowsingAuditTrail.objects.all().count(), 1)

    def test_generate_random_password(self):
        logger.info('Testing test_generate_random_password...',
                    extra={'AppName': 'EasyAssist'})

        self.assertNotEqual(len(generate_random_password()), 0)

    def test_random_with_n_digits(self):
        logger.info('Testing test_random_with_n_digits...',
                    extra={'AppName': 'EasyAssist'})

        self.assertEqual(len(str(random_with_n_digits(4))), 4)

    def test_extract_authorization_params(self):
        logger.info('Testing test_extract_authorization_params...',
                    extra={'AppName': 'EasyAssist'})

        cobrowseio = CobrowseIO.objects.create()

        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_AUTHORIZATION=http_authorization)

        response = client.get("https://www.hdfccredila.com")
        request = response.wsgi_request

        self.assertEqual(extract_authorization_params(
            request)[0], str(cobrowseio))

    def test_save_agent_closing_comments_cobrowseio(self):
        logger.info('Testing test_save_agent_closing_comments_cobrowseio...',
                    extra={'AppName': 'EasyAssist'})

        cobrowseio = CobrowseIO.objects.create()
        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        save_agent_closing_comments_cobrowseio(
            cobrowseio,
            cobrowse_agent,
            "comment",
            CobrowseAgentComment,
            "description"
        )

        agent_comment = CobrowseAgentComment.objects.filter(
            cobrowse_io=cobrowseio,
            agent=cobrowse_agent,
            agent_comments="comment",
            comment_desc="description",
        ).first()

        self.assertNotEqual(agent_comment, None)

    def test_get_visited_page_title_list_with_agent(self):
        logger.info('Testing test_get_visited_page_title_list_with_agent...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        CobrowseIO.objects.create(
            full_name='First Customer',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_archived=True,
            is_helpful=False,
            title="Apply for Education Loan | HDFC Credila Education Loan")

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_archived=True,
            is_helpful=True,
            title="ICICI Bank")

        CobrowseIO.objects.create(
            full_name='Third Customer',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_archived=True,
            is_helpful=False,
            cobrowsing_start_datetime=datetime.now(),
            title="Atcoder")

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_archived=True,
            is_helpful=True,
            title="Codechef")

        self.assertEqual(len(get_visited_page_title_list_with_agent(
            cobrowse_agent, CobrowseIO)), 4)

    def test_save_system_audit_trail(self):
        logger.info('Testing test_save_system_audit_trail...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        cobrowseio = CobrowseIO.objects.create()

        save_system_audit_trail(
            "category",
            "description",
            cobrowseio,
            cobrowse_agent.get_access_token_obj(),
            cobrowse_agent
        )

        audit_trail = SystemAuditTrail.objects.filter(
            category="category",
            description="description",
            cobrowse_io=cobrowseio,
            cobrowse_access_token=cobrowse_agent.get_access_token_obj(),
            sender=cobrowse_agent
        )

        self.assertNotEqual(audit_trail, None)

    def test_add_users_from_excel_document(self):
        logger.info('Testing test_add_users_from_excel_document...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        response = add_users_from_excel_document(
            "files/test/user_create_test.xlsx", cobrowse_agent, User, CobrowseAgent, LanguageSupport, ProductCategory, CobrowsingFileAccessManagement)

        self.assertEqual(response['status'], 200)

        lang_hindi = LanguageSupport.objects.get(title="Hindi")
        lang_gujarati = LanguageSupport.objects.get(title="Gujarati")
        lang_marathi = LanguageSupport.objects.get(title="Marathi")

        cat_car_loan = ProductCategory.objects.get(title="Car loan")
        cat_home_loan = ProductCategory.objects.get(title="Home loan")

        agent1 = CobrowseAgent.objects.filter(
            user__username="agent1@gmail.com",
            mobile_number="9512395123",
            user__first_name="Agent One",
            role="agent",
            supported_language=lang_hindi,
            product_category=cat_car_loan
        ).first()

        supervisor1 = CobrowseAgent.objects.filter(
            user__username="supervisor1@gmail.com",
            mobile_number="9512395124",
            user__first_name="Supervisor One",
            role="supervisor",
            supported_language=lang_gujarati,
            product_category=cat_home_loan
        ).first()

        agent2 = CobrowseAgent.objects.filter(
            user__username="agent2@gmail.com",
            mobile_number="9512395125",
            user__first_name="Agent Two",
            role="agent",
            supported_language=lang_marathi,
            product_category=cat_home_loan
        ).first()

        self.assertNotEqual(agent1, None)
        self.assertNotEqual(supervisor1, None)
        self.assertNotEqual(agent2, None)

    def test_create_excel_wrong_user_data(self):
        logger.info('Testing test_create_excel_wrong_user_data...',
                    extra={'AppName': 'EasyAssist'})

        file_path = create_excel_wrong_user_data([
            {
                'row_num': 1,
                'detail': 'details',
                'data_array': ['A', 'B']
            }
        ])

        self.assertNotEqual(file_path, None)
