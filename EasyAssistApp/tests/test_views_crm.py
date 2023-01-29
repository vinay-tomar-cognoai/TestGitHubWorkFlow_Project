from django.test import TestCase
from django.test import Client
from EasyChatApp.models import Supervisor, User
from EasyAssistApp.models import *
import base64


class CRM(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: CRM...', extra={
                    'AppName': 'EasyAssist'})
        user = User.objects.create(username='testeasyassist@example.com',
                                   email='testeasyassist@example.com', password='testeasyassist')
        support_user = \
            User.objects.create(username='support_testeasyassist@example.com',
                                email='support_testeasyassist@example.com', password='testeasyassist')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasyassist@example.com',
                                email='supervisor_testeasyassist@example.com', password='testeasyassist')

        adminally_user = \
            User.objects.create(username='adminally_testeasyassist@example.com',
                                email='adminally_testeasyassist@example.com', password='testeasyassist')

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

        cobrowse_agent = CobrowseAgent.objects.create(user=adminally_user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'admin_ally'
        cobrowse_agent.save()

    def get_auth_token(self):
        username = 'testeasyassist@example.com'
        password = 'testeasyassist'

        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' +
                        base64.b64encode((username + ':' + password).encode()).decode()}

        client = Client()
        request = client.post('/easy-assist/crm/generate-auth-token/',
                              json.dumps({}),
                              content_type='application/json',
                              **auth_headers)

        response_data = request.data
        return response_data["Body"]["auth_token"]

    def test_CRMGenerateAuthTokenAPI(self):
        logger.info('Testing test_CRMGenerateAuthTokenAPI...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()
        integration_obj = CRMIntegrationModel.objects.filter(
            auth_token=auth_token).first()

        self.assertNotEqual(integration_obj, None)

        cobrowse_agent = CobrowseAgent.objects.filter(
            user__username='testeasyassist@example.com').first()
        access_token = cobrowse_agent.get_access_token_obj()
        self.assertEqual(integration_obj.access_token, access_token)


class CRMCreateUserAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCreateUserAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMCreateUserAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMCreateUserAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        user_email = "support_testeasyassist@example.com"
        data = {
            "user_email": user_email,
            "user_name": "Test Xyz",
            "user_mobile": "9988998899",
            # "support_level": "L1",
            "user_type": "agent",
            "supervisor_list": ["testeasyassist@example.com", "supervisor_testeasyassist@example.com"],
            "language_list": ["Hindi", "Gujarati"],
            # "product_category_list": ["Car Loan", "Home Loan"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_wrongInput(self):
        logger.info('Testing CRMCreateUserAPI test_wrongInput...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        user_email = "support_testeasyassist@example.com"
        data = {
            "user_email": user_email,
            "user_name": "",
            "user_mobile": "998899889",
            "support_level": "L10",
            "user_type": "admin_agent",
            "supervisor_list": ["supervisor_testeasyassist@example.com"],
            "language_list": ["Gujarati", "l"],
            "product_category_list": ["Car Loan", "h"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 302)

    def test_success_adminally(self):
        logger.info('Testing CRMCreateUserAPI test_success_adminally...', extra={
                    'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()

        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        user_email = "adminally_testeasyassist1@example.com"
        data = {
            "user_email": user_email,
            "user_name": "Test Admin ally Xyz",
            "user_mobile": "9988998899",
            "user_type": "admin_ally",
            "supervisor_list": ["supervisor_testeasyassist@example.com"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        new_agent_obj = CobrowseAgent.objects.get(
            user__username__iexact=user_email)
        self.assertEqual(new_agent_obj.mobile_number, "9988998899")
        self.assertEqual(new_agent_obj.role, "admin_ally")

        self.assertIn(new_agent_obj, admin_agent.agents.all())

        access_token_obj = new_agent_obj.get_access_token_obj()
        if access_token_obj.allow_language_support:
            lang_obj_1 = LanguageSupport.objects.filter(
                title__iexact="LangOne").first()
            lang_obj_2 = LanguageSupport.objects.filter(
                title__iexact="LangTwo").first()

            self.assertNotEqual(lang_obj_1, None)
            self.assertNotEqual(lang_obj_2, None)

            self.assertIn(lang_obj_1, new_agent_obj.supported_language.all())
            self.assertIn(lang_obj_2, new_agent_obj.supported_language.all())

        if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
            category_obj_1 = ProductCategory.objects.filter(
                title__iexact="Car Loan").first()
            category_obj_2 = ProductCategory.objects.filter(
                title__iexact="Home Loan").first()

            self.assertNotEqual(category_obj_1, None)
            self.assertNotEqual(category_obj_2, None)

            self.assertIn(category_obj_1, new_agent_obj.product_category.all())
            self.assertIn(category_obj_2, new_agent_obj.product_category.all())

    def test_success_supervisor(self):
        logger.info('Testing CRMCreateUserAPI test_success_supervisor...', extra={
                    'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        adminally_agent = CobrowseAgent.objects.filter(
            user__username="adminally_testeasyassist@example.com").first()
        admin_agent.agents.add(adminally_agent)
        admin_agent.save()

        for language_obj in admin_agent.supported_language.all():
            adminally_agent.supported_language.add(language_obj)
            adminally_agent.save()

        for product_category_obj in admin_agent.product_category.all():
            adminally_agent.product_category.add(product_category_obj)
            adminally_agent.save()

        user_email = "supervisor_testeasyassist1@example.com"
        data = {
            "user_email": user_email,
            "user_name": "Test Supervisor Xyz",
            "user_mobile": "9988998899",
            "support_level": "L1",
            "user_type": "supervisor",
            "language_list": ["LangOne", "LangTwo"],
            "product_category_list": ["Car Loan", "Home Loan"],
            "assign_followup_lead_to_agent": True,
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        new_agent_obj = CobrowseAgent.objects.get(
            user__username__iexact=user_email)
        self.assertEqual(new_agent_obj.mobile_number, "9988998899")
        self.assertEqual(new_agent_obj.support_level, "L1")
        self.assertEqual(new_agent_obj.role, "supervisor")

        self.assertIn(new_agent_obj, admin_agent.agents.all())

        access_token_obj = new_agent_obj.get_access_token_obj()
        if access_token_obj.allow_language_support:
            lang_obj_1 = LanguageSupport.objects.filter(
                title__iexact="LangOne").first()
            lang_obj_2 = LanguageSupport.objects.filter(
                title__iexact="LangTwo").first()

            self.assertNotEqual(lang_obj_1, None)
            self.assertNotEqual(lang_obj_2, None)

            self.assertIn(lang_obj_1, new_agent_obj.supported_language.all())
            self.assertIn(lang_obj_2, new_agent_obj.supported_language.all())

        if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
            category_obj_1 = ProductCategory.objects.filter(
                title__iexact="Car Loan").first()
            category_obj_2 = ProductCategory.objects.filter(
                title__iexact="Home Loan").first()

            self.assertNotEqual(category_obj_1, None)
            self.assertNotEqual(category_obj_2, None)

            self.assertIn(category_obj_1, new_agent_obj.product_category.all())
            self.assertIn(category_obj_2, new_agent_obj.product_category.all())

    def test_success_agent(self):
        logger.info('Testing CRMCreateUserAPI test_success_agent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        user_email = "support_testeasyassist1@example.com"
        data = {
            "user_email": user_email,
            "user_name": "Test Xyz",
            "user_mobile": "9988998899",
            "support_level": "L1",
            "user_type": "agent",
            "supervisor_list": ["supervisor_testeasyassist@example.com"],
            "language_list": ["LangOne", "LangTwo"],
            "product_category_list": ["Car Loan", "Home Loan"],
            "assign_followup_lead_to_agent": True,
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        new_agent_obj = CobrowseAgent.objects.get(
            user__username__iexact=user_email)
        self.assertEqual(new_agent_obj.mobile_number, "9988998899")
        self.assertEqual(new_agent_obj.support_level, "L1")
        self.assertEqual(new_agent_obj.role, "agent")

        self.assertIn(new_agent_obj, supervisor_agent.agents.all())

        access_token_obj = new_agent_obj.get_access_token_obj()
        if access_token_obj.allow_language_support:
            lang_obj_1 = LanguageSupport.objects.filter(
                title__iexact="LangOne").first()
            lang_obj_2 = LanguageSupport.objects.filter(
                title__iexact="LangTwo").first()

            self.assertNotEqual(lang_obj_1, None)
            self.assertNotEqual(lang_obj_2, None)

            self.assertIn(lang_obj_1, new_agent_obj.supported_language.all())
            self.assertIn(lang_obj_2, new_agent_obj.supported_language.all())

        if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
            category_obj_1 = ProductCategory.objects.filter(
                title__iexact="Car Loan").first()
            category_obj_2 = ProductCategory.objects.filter(
                title__iexact="Home Loan").first()

            self.assertNotEqual(category_obj_1, None)
            self.assertNotEqual(category_obj_2, None)

            self.assertIn(category_obj_1, new_agent_obj.product_category.all())
            self.assertIn(category_obj_2, new_agent_obj.product_category.all())


class CRMUpdateUserAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMUpdateUserAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMUpdateUserAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/update-user/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMUpdateUserAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "user_email": "support_testeasyassist@example.com",
            "user_name": "Test Xyz",
            "user_mobile": "9988998899",
            "support_level": "L1",
            "user_type": "agent",
            "supervisor_list": ["testeasyassist@example.com", "supervisor_testeasyassist@example.com"],
            "language_list": ["Hindi", "Gujarati"],
            "product_category_list": ["Car Loan", "Home Loan"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/update-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_wrongInput(self):
        logger.info('Testing CRMUpdateUserAPI test_wrongInput...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        user_email = "support_testeasyassist@example.com"
        data = {
            "user_email": user_email,
            "user_name": "",
            "user_mobile": "998899889",
            "support_level": "L10",
            "user_type": "admin_agent",
            "supervisor_list": ["supervisor_testeasyassist@example.com"],
            "language_list": ["Gujarati", "l"],
            "product_category_list": ["Car Loan", "h"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/update-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 302)

    def test_success(self):
        logger.info('Testing CRMUpdateUserAPI test_success...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()
        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        user_email = str(supervisor_agent.user.username)

        data = {
            "user_email": user_email,
            "support_level": "L2",
            "language_list": ["LangOne", "LangTwo"],
            "product_category_list": ["Car Loan", "Home Loan"],
            "assign_followup_lead_to_agent": False,
        }

        client = Client()
        request = client.post('/easy-assist/crm/update-user/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        self.assertEqual(supervisor_agent.support_level, "L2")
        self.assertEqual(supervisor_agent.role, "supervisor")
        self.assertEqual(supervisor_agent.assign_followup_leads, False)

        self.assertIn(supervisor_agent, admin_agent.agents.all())

        access_token_obj = admin_agent.get_access_token_obj()
        if access_token_obj.allow_language_support:
            lang_obj_1 = LanguageSupport.objects.filter(
                title__iexact="LangOne").first()
            lang_obj_2 = LanguageSupport.objects.filter(
                title__iexact="LangTwo").first()

            self.assertNotEqual(lang_obj_1, None)
            self.assertNotEqual(lang_obj_2, None)

            self.assertIn(lang_obj_1, admin_agent.supported_language.all())
            self.assertIn(lang_obj_2, admin_agent.supported_language.all())

            self.assertIn(
                lang_obj_1, supervisor_agent.supported_language.all())
            self.assertIn(
                lang_obj_2, supervisor_agent.supported_language.all())

        if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
            category_obj_1 = ProductCategory.objects.filter(
                title__iexact="Car Loan").first()
            category_obj_2 = ProductCategory.objects.filter(
                title__iexact="Home Loan").first()

            self.assertNotEqual(category_obj_1, None)
            self.assertNotEqual(category_obj_2, None)

            self.assertIn(category_obj_1, admin_agent.product_category.all())
            self.assertIn(category_obj_2, admin_agent.product_category.all())

            self.assertIn(category_obj_1,
                          supervisor_agent.product_category.all())
            self.assertIn(category_obj_2,
                          supervisor_agent.product_category.all())


class CRMChangeAgentStatusAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMChangeAgentStatusAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMChangeAgentStatusAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/change-user-status/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMChangeAgentStatusAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "user_email": "support_testeasyassist@example.com",
            # "is_active": False,
            # "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing CRMChangeAgentStatusAPI test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": "new_user@example.com",
            "is_active": False,
            "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success_true(self):
        logger.info('Testing CRMChangeAgentStatusAPI test_success_true...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()
        new_agent_obj = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()
        new_agent_obj.is_account_active = False
        new_agent_obj.save()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        supervisor_agent.agents.add(new_agent_obj)
        supervisor_agent.save()

        data = {
            "user_email": new_agent_obj.user.username,
            "is_account_active": True
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        new_agent_obj = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()
        self.assertEqual(new_agent_obj.is_account_active, True)

    def test_success_false(self):
        logger.info('Testing CRMChangeAgentStatusAPI test_success_false...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()
        new_agent_obj = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()
        new_agent_obj.is_account_active = True
        new_agent_obj.save()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        supervisor_agent.agents.add(new_agent_obj)
        supervisor_agent.save()

        data = {
            "user_email": new_agent_obj.user.username,
            "is_active": True,
            "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        new_agent_obj = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()
        self.assertEqual(new_agent_obj.is_active, False)
        self.assertEqual(new_agent_obj.is_account_active, False)


class CRMUserStatusAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMUserStatusAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/get-user-status/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMUserStatusAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "user_email": "support_testeasyassist@example.com"
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing CRMUserStatusAPI test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": "new_user@example.com",
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success(self):
        logger.info('Testing CRMUserStatusAPI test_success...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": "supervisor_testeasyassist@example.com",
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-user-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)


class CRMAllUsersStatusAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAllUsersStatusAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMAllUsersStatusAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMAllUsersStatusAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "user_email": "support_testeasyassist@example.com"
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing CRMAllUsersStatusAPI test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": "new_user@example.com",
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success_adminally(self):
        logger.info('Testing CRMAllUsersStatusAPI test_success_adminally...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        adminally_agent = CobrowseAgent.objects.filter(
            user__username="adminally_testeasyassist@example.com").first()

        admin_agent.agents.add(adminally_agent)
        admin_agent.save()

        data = {
            "user_email": str(adminally_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_success_supervisor(self):
        logger.info('Testing CRMAllUsersStatusAPI test_success_supervisor...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": str(supervisor_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_fail_agent(self):
        logger.info('Testing CRMAllUsersStatusAPI test_fail_agent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-all-users-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 402)


class CRMGetListOfUsersAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMGetListOfUsersAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMGetListOfUsersAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMGetListOfUsersAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "user_email": "support_testeasyassist@example.com"
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing CRMGetListOfUsersAPI test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": "new_user@example.com",
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success_adminally(self):
        logger.info('Testing CRMGetListOfUsersAPI test_success_adminally...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        adminally_agent = CobrowseAgent.objects.filter(
            user__username="adminally_testeasyassist@example.com").first()

        admin_agent.agents.add(adminally_agent)
        admin_agent.save()

        data = {
            "user_email": str(adminally_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_success_supervisor(self):
        logger.info('Testing CRMGetListOfUsersAPI test_success_supervisor...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": str(supervisor_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_fail_agent(self):
        logger.info('Testing CRMGetListOfUsersAPI test_fail_agent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
        }

        client = Client()
        request = client.post('/easy-assist/crm/get-list-of-users/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 402)


class CRMChangeUserPasswordAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMChangeUserPasswordAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing CRMChangeUserPasswordAPI test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "user_email": "support_testeasyassist@example.com",
            "old_password": "Abcd@123456",
            # "new_password": "Abcd@123456"
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "user_email": "new_user@example.com",
            "old_password": "Abcd@123456",
            "new_password": "Abcd@123456"
        }

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success_adminally(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_success_adminally...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        adminally_user = CobrowseAgent.objects.filter(
            user__username="adminally_testeasyassist@example.com").first()

        admin_agent.agents.add(adminally_user)
        admin_agent.save()

        data = {
            "user_email": str(adminally_user.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@12345"
        }

        user_obj = adminally_user.user
        user_obj.set_password(data["old_password"])
        user_obj.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_success_supervisor(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_success_supervisor...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        supervisor_agent = CobrowseAgent.objects.filter(
            user__username="supervisor_testeasyassist@example.com").first()

        admin_agent.agents.add(supervisor_agent)
        admin_agent.save()

        data = {
            "user_email": str(supervisor_agent.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@12345"
        }

        user_obj = supervisor_agent.user
        user_obj.set_password(data["old_password"])
        user_obj.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_success_agent(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_success_agent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@12345"
        }

        user_obj = support_agent.user
        user_obj.set_password(data["old_password"])
        user_obj.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

    def test_agent_incorrect_password(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_agent_incorrect_password...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@12345"
        }

        user_obj = support_agent.user
        user_obj.set_password("Abcd@1234567")
        user_obj.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 302)

    def test_agent_same_passwords(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_agent_same_passwords...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@123456"
        }

        user_obj = support_agent.user
        user_obj.set_password(data["old_password"])
        user_obj.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 302)

    def test_agent_daily_limit_exhausted(self):
        logger.info('Testing CRMChangeUserPasswordAPI test_agent_daily_limit_exhausted...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        admin_agent = CobrowseAgent.objects.filter(
            user__username="testeasyassist@example.com").first()
        support_agent = CobrowseAgent.objects.filter(
            user__username="support_testeasyassist@example.com").first()

        admin_agent.agents.add(support_agent)
        admin_agent.save()

        data = {
            "user_email": str(support_agent.user.username),
            "old_password": "Abcd@123456",
            "new_password": "Abcd@123456"
        }

        user_obj = support_agent.user
        user_obj.set_password(data["old_password"])
        user_obj.save()

        support_agent.last_password_resend_date = timezone.now()
        support_agent.resend_password_count = -1
        support_agent.save()

        client = Client()
        request = client.post('/easy-assist/crm/change-user-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 307)
