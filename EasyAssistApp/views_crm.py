from rest_framework.views import APIView
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from rest_framework.response import Response
from EasyChatApp.models import User
from EasyAssistApp.utils_crm import *
from rest_framework.authentication import BasicAuthentication


class CRMCreateUserAPI(APIView):

    def validate_request_data(self, request_data, access_token_obj, active_agent):

        validation_response = {
            "status": "VALID",
            "ValidatorResult": {
                "user_name": "-",
                "user_email": "-",
                "user_mobile": "-",
                "platform_url": "-",
                "user_type": "-",
                "support_level": "-",
                "supervisor_list": "-",
                "language_list": "-",
                "product_category_list": "-",
                "assign_followup_lead_to_agent": "-",
            }
        }
        try:
            is_status_invalid = False
            agent_email = request_data["user_email"]
            agent_email = sanitize_input_string(agent_email)

            if not is_email_valid(agent_email):
                validation_response["ValidatorResult"]["user_email"] = "Please enter valid user email."
                is_status_invalid = True

            if not is_status_invalid:
                cobrowse_agent = CobrowseAgent.objects.filter(
                    user__username__iexact=agent_email).first()

                if cobrowse_agent:
                    validation_response["ValidatorResult"]["user_email"] = "Email ID already exists"
                    is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["user_email"] = agent_email

            agent_name = request_data["user_name"]
            agent_name = sanitize_input_string(agent_name)
            reg_name = r'^[a-zA-Z ]*$'

            if len(agent_name) <= 1:
                validation_response["ValidatorResult"]["user_name"] = "Name should be atleast 2 characters"
                is_status_invalid = True
            else:
                if not re.fullmatch(reg_name, agent_name):
                    validation_response["ValidatorResult"][
                        "user_name"] = "Please enter valid name (only A-Z, a-z and space are allowed)"
                    is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["user_name"] = agent_name

            agent_mobile = ""
            if "user_mobile" in request_data:
                agent_mobile = request_data["user_mobile"]
                agent_mobile = sanitize_input_string(agent_mobile)

                cobrowse_agent = CobrowseAgent.objects.filter(
                    mobile_number=agent_mobile).first()

                if not is_mobile_valid(agent_mobile):
                    validation_response["ValidatorResult"]["user_mobile"] = "Expected 10 digit"
                    is_status_invalid = True
                elif cobrowse_agent:
                    validation_response["ValidatorResult"]["user_mobile"] = "Mobile number already exists"
                    is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["user_mobile"] = agent_mobile

            agent_type = sanitize_input_string(request_data["user_type"])
            agent_type = agent_type.strip().lower()
            if agent_type in ["agent", "supervisor", "admin_ally"]:
                validation_response["ValidatorResult"]["user_type"] = agent_type
            else:
                validation_response["ValidatorResult"]["user_type"] = "Expected from ['agent', 'supervisor', 'admin_ally']"
                is_status_invalid = True

            if agent_type in ["agent", "supervisor"]:
                support_level = sanitize_input_string(
                    request_data["support_level"])
                support_level = support_level.strip().lower()
                if support_level in ["l1", "l2", "l3"]:
                    validation_response["ValidatorResult"]["support_level"] = support_level
                else:
                    validation_response["ValidatorResult"]["support_level"] = "Expected from ['L1', 'L2', 'L3']"
                    is_status_invalid = True

            if agent_type in ["admin_ally", "agent"]:
                if active_agent.role != "supervisor":
                    supervisor_list = request_data["supervisor_list"]
                    if not is_supervisor_list_valid(supervisor_list, validation_response, active_agent):
                        is_status_invalid = True
                    else:
                        validation_response["ValidatorResult"]["supervisor_list"] = supervisor_list
                else:
                    validation_response["ValidatorResult"]["supervisor_list"] = str(
                        active_agent.user.username)

            platform_url = sanitize_input_string(request_data["platform_url"])
            if not is_url_valid(platform_url):
                validation_response["ValidatorResult"]["platform_url"] = "Invalid platform URL"
                is_status_invalid = True
            else:
                validation_response["ValidatorResult"]["platform_url"] = platform_url

            if access_token_obj.allow_language_support:
                if "language_list" in request_data:
                    language_list = request_data["language_list"]
                    if not is_language_list_valid(language_list, validation_response, active_agent):
                        is_status_invalid = True
                    else:
                        validation_response["ValidatorResult"]["language_list"] = language_list

            if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
                if "product_category_list" in request_data:
                    product_category_list = request_data["product_category_list"]
                    if not is_product_category_list_valid(product_category_list, validation_response, active_agent):
                        is_status_invalid = True
                    else:
                        validation_response["ValidatorResult"]["product_category_list"] = product_category_list

            if access_token_obj.enable_followup_leads_tab and agent_type in ["supervisor", "agent"]:
                if "assign_followup_lead_to_agent" not in request_data:
                    validation_response["ValidatorResult"]["assign_followup_lead_to_agent"] = "Missing assigning of followup lead to agent"
                    is_status_invalid = True
                else:
                    if request_data["assign_followup_lead_to_agent"] in [True, False]:
                        validation_response["ValidatorResult"]["assign_followup_lead_to_agent"] = request_data["assign_followup_lead_to_agent"]
                    else:
                        validation_response["ValidatorResult"]["assign_followup_lead_to_agent"] = "Value for assinging of followup lead to agent should be a boolean"
                        is_status_invalid = True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error validate_request_data %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            is_status_invalid = True

        if is_status_invalid:
            validation_response["status"] = "INVALID"

        return validation_response

    def create_new_agent(self, request, request_data, access_token_obj, active_agent):
        try:
            agent_creation_response = {
                "status": 500,
                "Description": INTERNAL_SERVER_ERROR_MSG,
                "CreationResult": {
                    "language_list": "-",
                    "product_category_list": "-",
                    "supervisor_list": "-",
                }
            }

            is_status_invalid = False

            agent_name = sanitize_input_string(request_data["user_name"])
            agent_email = sanitize_input_string(request_data["user_email"])
            agent_type = sanitize_input_string(
                request_data["user_type"]).strip().lower()
            platform_url = sanitize_input_string(request_data["platform_url"])

            if agent_type == "agent" and active_agent.is_agent_creation_limit_exhausted():
                agent_creation_response["status"] = 307
                agent_creation_response["Description"] = AGENT_CREATION_LIMIT_EXHAUST_ERROR
                return agent_creation_response

            if agent_type == "supervisor" and active_agent.is_supervisor_creation_limit_exhausted():
                agent_creation_response["status"] = 307
                agent_creation_response["Description"] = SUPERVISOR_CREATION_LIMIT_EXHAUST_ERROR
                return agent_creation_response

            agent_mobile = None
            if "user_mobile" in request_data:
                agent_mobile = sanitize_input_string(
                    request_data["user_mobile"])

            language_list = []
            language_pk_list = []

            if access_token_obj.allow_language_support and "language_list" in request_data:
                language_list = [sanitize_input_string(language).strip(
                ) for language in request_data["language_list"]]
                for language in language_list:
                    language_support_obj = active_agent.supported_language.filter(
                        title__iexact=language).first()
                    language_pk_list.append(language_support_obj.pk)

            product_category_list = []
            product_category_pk_list = []

            if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
                if "product_category_list" in request_data:
                    product_category_list = [sanitize_input_string(product_category).strip(
                    ) for product_category in request_data["product_category_list"]]
                    for product_category in product_category_list:
                        product_category_obj = active_agent.product_category.filter(
                            title__iexact=product_category).first()
                        product_category_pk_list.append(
                            product_category_obj.pk)

            support_level = "L1"
            if agent_type in ["agent", "supervisor"]:
                support_level = sanitize_input_string(
                    request_data["support_level"]).strip()
                support_level = support_level[0].upper() + support_level[1:]

            supervisor_list = []
            supervisor_pk_list = []

            if agent_type in ["admin_ally", "agent"]:
                if active_agent.role != "supervisor":
                    supervisor_list = request_data["supervisor_list"]
                    for supervisor in supervisor_list:
                        supervisor = sanitize_input_string(supervisor).strip()
                        supervisor_obj = active_agent.agents.filter(
                            user__username__iexact=supervisor, role="supervisor").first()
                        supervisor_pk_list.append(supervisor_obj.pk)
                else:
                    supervisor_pk_list = [-1]
            elif agent_type == "supervisor":
                supervisor_pk_list = [-1]

            if is_status_invalid:
                return agent_creation_response

            assign_followup_lead_to_agent = True
            if access_token_obj.enable_followup_leads_tab and "assign_followup_lead_to_agent" in request_data:
                assign_followup_lead_to_agent = request_data["assign_followup_lead_to_agent"]

            category_matched = check_for_supervisor_category_language_match(active_agent, agent_type, supervisor_pk_list, language_pk_list,
                                                                            product_category_pk_list, CobrowseAgent)

            if len(category_matched):
                agent_type_readable = "admin ally" if agent_type == "admin_ally" else "agent"

                if category_matched["matched_error"] == "language":
                    agent_creation_response["CreationResult"]["language_list"] = "Supported language mismatch detected between supervisor " + \
                        category_matched["supervisor"] + \
                        " and entered " + agent_type_readable + ". Please update and try again."
                else:
                    agent_creation_response["CreationResult"]["product_category_list"] = "Product category mismatch detected between supervisor " + \
                        category_matched["supervisor"] + \
                        " and entered " + agent_type_readable + ". Please update and try again."

                agent_creation_response["status"] = 313
                agent_creation_response["Description"] = "Language/Product category mismatch"
                return agent_creation_response

            user = None
            try:
                user = User.objects.get(username__iexact=agent_email)
                user.email = agent_email
                user.save()
            except Exception:
                user = User.objects.create(first_name=agent_name,
                                           email=agent_email,
                                           username=agent_email,
                                           status="2",
                                           role="bot_builder")

                password = generate_password(access_token_obj.password_prefix)
                user.set_password(password)
                user.save()

            thread = threading.Thread(target=send_password_over_email, args=(
                agent_email, agent_name, password, platform_url, ), daemon=True)
            thread.start()

            cobrowse_agent = CobrowseAgent.objects.create(user=user,
                                                          mobile_number=agent_mobile,
                                                          role=agent_type.lower(),
                                                          support_level=support_level.upper(),
                                                          assign_followup_leads=assign_followup_lead_to_agent,
                                                          access_token=access_token_obj)

            update_agents_supervisors_creation_count(active_agent, agent_type.lower())

            add_selected_supervisor(
                supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)
            add_supported_language(
                cobrowse_agent, language_pk_list, LanguageSupport)
            add_product_category_to_user(
                cobrowse_agent, product_category_pk_list, ProductCategory)

            try:
                description = "New " + agent_type + \
                    " (" + agent_name + ") has been added through CRM API"
                save_audit_trail(
                    active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Add-User",
                    description,
                    json.dumps(request_data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMCreateAgentAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            agent_creation_response["status"] = 200
            agent_creation_response["Description"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error create_new_agent %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return agent_creation_response

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = crm_integration_model.agent

            if active_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMCreateUserAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            if "platform_url" not in request_data or len(request_data["platform_url"].strip()) == 0:
                request_data["platform_url"] = settings.EASYCHAT_HOST_URL

            is_all_data_available = True
            required_inputs = [
                "user_type",
                "user_name",
                "user_email",
                "platform_url",
            ]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False
                    break

            if is_all_data_available:
                agent_type = request_data["user_type"].lower()

                if active_agent.role == "supervisor":
                    if agent_type != "agent":
                        response["Head"]["ResponseCode"] = 303
                        response["Head"]["Description"] = "Unauthorized access."
                        return Response(data=response)
                elif active_agent.role == "admin_ally":
                    if agent_type not in ["supervisor", "agent"]:
                        response["Head"]["ResponseCode"] = 303
                        response["Head"]["Description"] = "Unauthorized access."
                        return Response(data=response)

            if is_all_data_available and access_token_obj.enable_followup_leads_tab:
                if agent_type in ["agent", "supervisor"] and "assign_followup_lead_to_agent" not in request_data:
                    is_all_data_available = False

            if is_all_data_available and agent_type in ["agent", "supervisor"]:
                if "support_level" not in request_data:
                    is_all_data_available = False

            if is_all_data_available and agent_type in ["admin_ally", "agent"]:
                if active_agent.role != "supervisor":
                    if "supervisor_list" not in request_data:
                        is_all_data_available = False

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            validation_response = self.validate_request_data(
                request_data, access_token_obj, active_agent)
            if validation_response["status"] == "INVALID":
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Invalid Input"
                response["Body"]["ValidatorResult"] = validation_response["ValidatorResult"]
                return Response(data=response)

            creation_response = self.create_new_agent(
                request, request_data, access_token_obj, active_agent)

            response["Head"]["ResponseCode"] = creation_response["status"]
            response["Head"]["Description"] = creation_response["Description"]

            if creation_response["status"] != 200:
                response["Body"] = creation_response["CreationResult"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCreateUserAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCreateUser = CRMCreateUserAPI.as_view()


class CRMUpdateUserAPI(APIView):

    def update_agent(self, request, request_data, access_token_obj, active_agent):
        try:
            agent_updation_response = {
                "status": 500,
                "Description": INTERNAL_SERVER_ERROR_MSG,
                "UpdationResult": {
                    "language_list": "-",
                    "product_category_list": "-",
                    "supervisor_list": "-",
                }
            }

            is_status_invalid = False
            platform_url = sanitize_input_string(request_data["platform_url"])
            agent_email = sanitize_input_string(request_data["user_email"])
            new_agent_email = agent_email

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__email=agent_email).first()
            agent_name = cobrowse_agent.user.first_name
            prev_role = cobrowse_agent.role
            agent_type = cobrowse_agent.role

            if "user_name" in request_data:
                agent_name = sanitize_input_string(request_data["user_name"])

            if "user_type" in request_data:
                agent_type = sanitize_input_string(
                    request_data["user_type"]).strip().lower()

            if "new_email_id" in request_data:
                new_agent_email = sanitize_input_string(
                    request_data["new_email_id"])

            if cobrowse_agent.role != agent_type and agent_type == "agent" and active_agent.is_agent_creation_limit_exhausted():
                agent_updation_response["status"] = 307
                agent_updation_response["Description"] = AGENT_CREATION_LIMIT_EXHAUST_ERROR
                return agent_updation_response

            if cobrowse_agent.role != agent_type and agent_type == "supervisor" and active_agent.is_supervisor_creation_limit_exhausted():
                agent_updation_response["status"] = 307
                agent_updation_response["Description"] = SUPERVISOR_CREATION_LIMIT_EXHAUST_ERROR
                return agent_updation_response

            language_list = []
            language_pk_list = []

            if access_token_obj.allow_language_support and "language_list" in request_data:
                language_list = [sanitize_input_string(language).strip(
                ) for language in request_data["language_list"]]
                for language in language_list:
                    language_support_obj = active_agent.supported_language.filter(
                        title__iexact=language).first()
                    language_pk_list.append(language_support_obj.pk)

            product_category_list = []
            product_category_pk_list = []

            if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
                if "product_category_list" in request_data:
                    product_category_list = [sanitize_input_string(product_category).strip(
                    ) for product_category in request_data["product_category_list"]]
                    for product_category in product_category_list:
                        product_category_obj = active_agent.product_category.filter(
                            title__iexact=product_category).first()
                        product_category_pk_list.append(
                            product_category_obj.pk)

            if agent_type != "agent":
                response_message = check_for_details_match(active_agent, agent_type, agent_email, language_pk_list,
                                                           product_category_pk_list, CobrowseAgent, User)

                if len(response_message):
                    agent_updation_response["status"] = 314
                    agent_updation_response["Description"] = "Language/Product category mismatched between some of the supervisors"
                    agent_updation_response["UpdationResult"][""] = response_message
                    return agent_updation_response

            supervisor_list = []
            supervisor_pk_list = []

            if agent_type in ["agent", "admin_ally"]:
                if "supervisor_list" not in request_data:
                    supervisor_list = cobrowse_agent.agents.filter(
                        role="supervisor").values_list('user__username', flat=True).distinct()
                else:
                    supervisor_list = request_data["supervisor_list"]

                if not len(supervisor_list):
                    supervisor_pk_list = [-1]

                for supervisor in supervisor_list:
                    supervisor = sanitize_input_string(supervisor).strip()
                    supervisor_obj = active_agent.agents.filter(
                        user__username__iexact=supervisor, role="supervisor").first()
                    supervisor_pk_list.append(supervisor_obj.pk)
            elif agent_type == "supervisor":
                supervisor_pk_list = [-1]

            if is_status_invalid:
                return agent_updation_response

            category_matched = check_for_supervisor_category_language_match(active_agent, agent_type, supervisor_pk_list, language_pk_list,
                                                                            product_category_pk_list, CobrowseAgent)

            if len(category_matched):

                agnet_type_readable = "admin ally" if agent_type == "admin_ally" else "agent"
                if category_matched["matched_error"] == "language":
                    agent_updation_response["UpdationResult"]["language_list"] = "Supported language mismatch detected between supervisor " + \
                        category_matched["supervisor"] + \
                        " and entered " + agnet_type_readable + ". Please update and try again."
                else:
                    agent_updation_response["UpdationResult"]["product_category_list"] = "Product category mismatch detected between supervisor " + \
                        category_matched["supervisor"] + \
                        " and entered " + agnet_type_readable + ". Please update and try again."

                agent_updation_response["status"] = 313
                agent_updation_response["Description"] = "Language/Product category mismatch"
                return agent_updation_response

            if cobrowse_agent.user.email != new_agent_email:
                password = generate_random_password()
                cobrowse_agent.user.set_password(password)
                cobrowse_agent.user.save()

                thread = threading.Thread(target=send_password_over_email, args=(
                    new_agent_email, agent_name, password, platform_url, ), daemon=True)
                thread.start()

            cobrowse_agent.user.first_name = agent_name
            cobrowse_agent.user.email = new_agent_email
            cobrowse_agent.user.username = new_agent_email

            if "user_mobile" in request_data:
                agent_mobile = sanitize_input_string(
                    request_data["user_mobile"])
                cobrowse_agent.mobile_number = agent_mobile

            support_level = cobrowse_agent.support_level
            if "support_level" in request_data:
                support_level = sanitize_input_string(
                    request_data["support_level"]).strip()
                support_level = support_level[0].upper() + support_level[1:]
                cobrowse_agent.support_level = support_level

            if "user_type" in request_data:
                agent_type = sanitize_input_string(
                    request_data["user_type"]).strip().lower()
                cobrowse_agent.role = agent_type

            assign_followup_lead_to_agent = True
            if access_token_obj.enable_followup_leads_tab and agent_type in ["agent", "supervisor"] and "assign_followup_lead_to_agent" in request_data:
                assign_followup_lead_to_agent = request_data["assign_followup_lead_to_agent"]
                cobrowse_agent.assign_followup_leads = assign_followup_lead_to_agent

            if agent_type == "supervisor":
                supervisors_objs = CobrowseAgent.objects.filter(
                    role="supervisor", agents=cobrowse_agent)
                for obj in supervisors_objs:
                    obj.agents.remove(cobrowse_agent)

            if agent_type == "agent":
                admin_agent = access_token_obj.agent
                agents = cobrowse_agent.agents.all()
                for agent in agents:
                    cobrowse_agent.agents.remove(agent)
                    cobrowse_agent.save()
                    supervisor_count = CobrowseAgent.objects.filter(
                        agents=agent).count()
                    if supervisor_count == 0:
                        admin_agent.agents.add(agent)
                        admin_agent.save()

            if active_agent.role == "admin" and agent_type == "agent":
                previous_supervisor_list = CobrowseAgent.objects.filter(
                    agents__pk=cobrowse_agent.pk).filter(~Q(role="admin_ally"))
                for previous_supervisor in previous_supervisor_list:
                    previous_supervisor.agents.remove(
                        cobrowse_agent)
                    previous_supervisor.save()

            if active_agent.role == "admin" and agent_type == "admin_ally":
                previous_supervisors_admin_ally = cobrowse_agent.agents.all()
                for previous_supervisor in previous_supervisors_admin_ally:
                    cobrowse_agent.agents.remove(
                        previous_supervisor)

            add_selected_supervisor(
                supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)

            cobrowse_agent.supported_language.clear()
            cobrowse_agent.product_category.clear()
            cobrowse_agent.user.save()
            cobrowse_agent.save()
            active_agent.save()
            add_supported_language(
                cobrowse_agent, language_pk_list, LanguageSupport)
            add_product_category_to_user(
                cobrowse_agent, product_category_pk_list, ProductCategory)

            if prev_role != agent_type:
                update_agents_supervisors_creation_count(active_agent, agent_type)

            description = "New Details for " + \
                agent_type + \
                " (" + agent_name + ") has been added"
            save_audit_trail(
                active_agent, COBROWSING_UPDATEUSER_ACTION, description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                active_agent.user,
                "Updated-User",
                description,
                json.dumps(request_data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            agent_updation_response["status"] = 200
            agent_updation_response["Description"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error update_agent %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return agent_updation_response

    def validate_request_data(self, request_data, access_token_obj, active_agent):
        try:
            validation_response = {
                "status": "VALID",
                "ValidatorResult": {
                    "user_name": "-",
                    "user_email": "-",
                    "user_mobile": "-",
                    "platform_url": "-",
                    "user_type": "-",
                    "support_level": "-",
                    "supervisor_list": "-",
                    "language_list": "-",
                    "product_category_list": "-",
                    "assign_followup_lead_to_agent": "-",
                    "new_email_id": "-",
                }
            }

            is_status_invalid = False
            agent_email = request_data["user_email"]
            agent_email = sanitize_input_string(agent_email)

            if not is_email_valid(agent_email):
                validation_response["ValidatorResult"]["user_email"] = "Please enter valid user email."
                is_status_invalid = True

            if not is_status_invalid:
                cobrowse_agent = CobrowseAgent.objects.filter(
                    user__username__iexact=agent_email).first()

                if cobrowse_agent:
                    if cobrowse_agent.role != "admin":
                        validation_response["ValidatorResult"]["user_email"] = str(
                            cobrowse_agent.user.email)
                    else:
                        validation_response["ValidatorResult"]["user_email"] = "Cannot able to modify admin account"
                        is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["user_email"] = "Agent not found"
                    is_status_invalid = True

            if "user_name" in request_data:
                agent_name = request_data["user_name"]
                agent_name = remo_special_tag_from_string(
                    remo_html_from_string(agent_name)).strip()
                reg_name = r'^[a-zA-Z ]*$'

                if len(agent_name) <= 1:
                    validation_response["ValidatorResult"]["user_name"] = "Name should be atleast 2 characters"
                    is_status_invalid = True
                else:
                    if not re.fullmatch(reg_name, agent_name):
                        validation_response["ValidatorResult"][
                            "user_name"] = "Please enter valid name (only A-Z, a-z and space are allowed)"
                        is_status_invalid = True
                    else:
                        validation_response["ValidatorResult"]["user_name"] = agent_name

            if "new_email_id" in request_data:
                new_email_id = remo_special_tag_from_string(
                    remo_html_from_string(request_data["new_email_id"])).strip()

                temp_cobrowse_agent = CobrowseAgent.objects.filter(
                    user__username__iexact=new_email_id).exclude(user=cobrowse_agent).first()

                if not is_email_valid(new_email_id):
                    validation_response["ValidatorResult"]["new_email_id"] = "Please enter valid user email."
                    is_status_invalid = True
                elif temp_cobrowse_agent:
                    validation_response["ValidatorResult"]["new_email_id"] = "Agent with the new agent email exists."
                    is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["new_email_id"] = new_email_id

            agent_mobile = ""
            if "user_mobile" in request_data:
                agent_mobile = request_data["user_mobile"]
                agent_mobile = sanitize_input_string(agent_mobile)

                temp_cobrowse_agent = CobrowseAgent.objects.filter(
                    mobile_number=agent_mobile).first()

                if not is_mobile_valid(agent_mobile):
                    validation_response["ValidatorResult"]["user_mobile"] = "Expected 10 digit"
                    is_status_invalid = True
                elif temp_cobrowse_agent:
                    validation_response["ValidatorResult"]["user_mobile"] = "Mobile number already exists"
                    is_status_invalid = True
                else:
                    validation_response["ValidatorResult"]["user_mobile"] = agent_mobile

            platform_url = sanitize_input_string(request_data["platform_url"])
            if not is_url_valid(platform_url):
                validation_response["ValidatorResult"]["platform_url"] = "Invalid platform URL"
                is_status_invalid = True
            else:
                validation_response["ValidatorResult"]["platform_url"] = platform_url

            if not is_status_invalid:
                if "user_type" in request_data:
                    agent_type = sanitize_input_string(
                        request_data["user_type"]).strip().lower()
                    if agent_type not in ["agent", "supervisor", "admin_ally"]:
                        validation_response["ValidatorResult"]["user_type"] = "Not allowed. Expected from ['agent', 'supervisor', 'admin_ally']"
                        is_status_invalid = True
                else:
                    agent_type = cobrowse_agent.role

                data_from_request = False
                if agent_type != cobrowse_agent.role:
                    data_from_request = True

                if active_agent.role == "admin" and cobrowse_agent.role == "admin_ally" and agent_type in ["agent", "supervisor"]:
                    validation_response["ValidatorResult"]["user_type"] = "Cannot able to change the user type for the adminally"
                    is_status_invalid = True

                if active_agent.role == "supervisor":
                    if agent_type != "agent":
                        validation_response["ValidatorResult"]["user_type"] = "Unauthorized access for changing of user role to " + agent_type
                        is_status_invalid = True
                    elif active_agent.agents.filter(user__username__iexact=agent_email).count() == 0:
                        validation_response["ValidatorResult"]["user"] = "Unauthorized access for the requested agent"
                        is_status_invalid = True

                if active_agent.role == "admin_ally":
                    if agent_type not in ["supervisor", "agent"]:
                        validation_response["ValidatorResult"]["user_type"] = "Unauthorized access for changing of user role " + agent_type
                        is_status_invalid = True
                    else:
                        is_under_me = False
                        if active_agent.agents.filter(user__username__iexact=agent_email).count():
                            is_under_me = True

                        if not is_under_me:
                            for agent in active_agent.agents.all():
                                if agent.agents.filter(user__username__iexact=agent_email).count():
                                    is_under_me = True

                                if is_under_me:
                                    break

                        if not is_under_me:
                            validation_response["ValidatorResult"]["user"] = "Unauthorized access for the requested agent"
                            is_status_invalid = True

                if agent_type in ["agent", "supervisor"]:
                    if "support_level" in request_data:
                        support_level = sanitize_input_string(
                            request_data["support_level"]).strip()

                        if support_level.lower() in ["l1", "l2", "l3"]:
                            validation_response["ValidatorResult"]["support_level"] = support_level.upper(
                            )
                        else:
                            validation_response["ValidatorResult"]["support_level"] = "Expected from ['L1', 'L2', 'L3']"
                            is_status_invalid = True
                    else:
                        support_level = cobrowse_agent.support_level

                if agent_type in ["agent", "admin_ally"]:
                    if "supervisor_list" not in request_data:
                        if data_from_request:
                            validation_response["ValidatorResult"]["supervisor_list"] = "Supervisor list cannot be empty"
                            is_status_invalid = True
                        else:
                            validation_response["ValidatorResult"]["supervisor_list"] = "Valid. Supervisor list not required for updating agent details"
                    else:
                        supervisor_list = request_data["supervisor_list"]
                        if not is_supervisor_list_valid(supervisor_list, validation_response, active_agent):
                            is_status_invalid = True
                        else:
                            validation_response["ValidatorResult"]["supervisor_list"] = supervisor_list

                if access_token_obj.allow_language_support and "language_list" in request_data:
                    language_list = request_data["language_list"]
                    if not is_language_list_valid(language_list, validation_response, active_agent):
                        is_status_invalid = True
                    else:
                        validation_response["ValidatorResult"]["language_list"] = language_list

                if access_token_obj.choose_product_category or access_token_obj.enable_tag_based_assignment_for_outbound:
                    if "product_category_list" in request_data:
                        product_category_list = request_data["product_category_list"]
                        if not is_product_category_list_valid(product_category_list, validation_response, active_agent):
                            is_status_invalid = True
                        else:
                            validation_response["ValidatorResult"]["product_category_list"] = product_category_list

                if access_token_obj.enable_followup_leads_tab and agent_type in ["agent", "supervisor"]:
                    if "assign_followup_lead_to_agent" in request_data:
                        if request_data["assign_followup_lead_to_agent"] in [True, False]:
                            validation_response["ValidatorResult"][
                                "assign_followup_lead_to_agent"] = request_data["assign_followup_lead_to_agent"]
                        else:
                            validation_response["ValidatorResult"]["assign_followup_lead_to_agent"] = "Value for assinging of followup lead to agent should be a boolean"
                            is_status_invalid = True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error validate_request_data %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            is_status_invalid = True

        if is_status_invalid:
            validation_response["status"] = "INVALID"

        return validation_response

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = crm_integration_model.agent

            if active_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMUpdateUserAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            if "platform_url" not in request_data or len(request_data["platform_url"].strip()) == 0:
                request_data["platform_url"] = settings.EASYCHAT_HOST_URL

            is_all_data_available = True
            required_inputs = [
                "user_email",
                "platform_url",
            ]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False
                    break

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            validation_response = self.validate_request_data(
                request_data, access_token_obj, active_agent)
            if validation_response["status"] == "INVALID":
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = 'Invalid input'
                response["Body"]['ValidatorResult'] = validation_response["ValidatorResult"]
                return Response(data=response)

            updation_response = self.update_agent(
                request, request_data, access_token_obj, active_agent)
            response["Head"]["ResponseCode"] = updation_response["status"]
            response["Head"]["Description"] = updation_response["Description"]

            if updation_response["status"] != 200:
                response["Body"] = updation_response["UpdationResult"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMUpdateAgentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMUpdateUser = CRMUpdateUserAPI.as_view()


class CRMChangeUserStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            active_agent = crm_integration_model.agent

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMChangeUserStatusAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            is_all_data_available = True
            required_inputs = ["user_email"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if "is_active" not in request_data and "is_account_active" not in request_data:
                is_all_data_available = False

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            agent_email = request_data["user_email"]
            agent_email = remo_special_tag_from_string(
                remo_html_from_string(agent_email)).strip()

            if not is_email_valid(agent_email):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Please enter valid user email."
                return Response(data=response)

            is_under_me = is_user_under_me(
                active_agent, agent_email, CobrowseAgent)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_email).first()

            if not is_under_me and cobrowse_agent and cobrowse_agent.role == "agent":
                if cobrowse_agent == active_agent:
                    is_under_me = True

            if not is_under_me:
                response["Head"]["ResponseCode"] = 303
                response["Head"]["Description"] = "Unauthorized access"
                return Response(data=response)

            change_active_status = False
            if "is_active" in request_data:
                is_active = request_data["is_active"]
                if is_active == True or is_active == False:
                    if cobrowse_agent.role == "agent":
                        if cobrowse_agent.is_account_active:
                            change_active_status = True
                        else:
                            response["Head"]["ResponseCode"] = 321
                            response["Head"]["Description"] = "Cannot able to change the Online/Offline status for a deactivated user."
                            return Response(data=response)
                    else:
                        response["Head"]["ResponseCode"] = 322
                        response["Head"]["Description"] = "Invalid Input. Status can able to change for only agents"
                        return Response(data=response)
                else:
                    response["Head"]["ResponseCode"] = 305
                    response["Head"]["Description"] = "Invalid Input. Please use boolean values"
                    return Response(data=response)

            change_account_active_status = False
            if "is_account_active" in request_data:
                if active_agent.role != "agent":
                    is_account_active = request_data["is_account_active"]
                    if is_account_active == True or is_account_active == False:
                        if is_account_active == False and cobrowse_agent.is_cobrowsing_active == True:
                            response["Head"]["ResponseCode"] = 304
                            response["Head"]["Description"] = "Agent is currently in co-browse session"
                            return Response(data=response)

                        if cobrowse_agent == active_agent:
                            response["Head"]["ResponseCode"] = 320
                            response["Head"]["Description"] = "Cannot able to change account status for your own account"
                            return Response(data=response)

                        agents_list = []
                        supervisors_list = []
                        admin_allys_list = []
                        if active_agent.role in ["admin", "admin_ally"]:
                            agents_list = get_list_agents_under_admin(
                                admin_user=active_agent, is_active=None, is_account_active=None)
                            supervisors_list = get_list_supervisor_under_admin(
                                admin_user=active_agent, is_active=None, is_account_active=None)
                            admin_allys_list = get_list_admin_ally(
                                active_agent, is_active=None, is_account_active=None)
                        else:
                            agents_list = list(active_agent.agents.all())

                        if cobrowse_agent in agents_list or cobrowse_agent in supervisors_list or cobrowse_agent in admin_allys_list:
                            change_account_active_status = True
                    else:
                        response["Head"]["ResponseCode"] = 305
                        response["Head"]["Description"] = "Invalid Input. Please use boolean values"
                        return Response(data=response)
                else:
                    response["Head"]["ResponseCode"] = 402
                    response["Head"]["Description"] = "This API is unauthorized for agents"
                    return Response(data=response)

            if change_active_status:
                change_agent_is_active_flag(
                    is_active, cobrowse_agent, CobrowseAgentOnlineAuditTrail, CobrowseAgentWorkAuditTrail)

            if change_account_active_status:
                change_agent_is_account_active_flag(
                    is_account_active, active_agent, cobrowse_agent, request, request_data, CobrowsingAuditTrail)

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentChangeStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMChangeUserStatus = CRMChangeUserStatusAPI.as_view()


class CRMUserStatusAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            active_agent = crm_integration_model.agent
            if active_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMUserStatusAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            is_all_data_available = True
            required_inputs = ["user_email"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            agent_email = request_data["user_email"]
            agent_email = remo_special_tag_from_string(
                remo_html_from_string(agent_email)).strip()

            if not is_email_valid(agent_email):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Please enter valid user email."
                return Response(data=response)

            is_under_me = is_user_under_me(
                active_agent, agent_email, CobrowseAgent)

            if not is_under_me:
                response["Head"]["ResponseCode"] = 303
                response["Head"]["Description"] = "Unauthorized access"
                return Response(data=response)

            cobrowse_agent_obj = CobrowseAgent.objects.filter(
                user__username__iexact=agent_email).first()

            if cobrowse_agent_obj.is_account_active:
                if cobrowse_agent_obj.role in ["admin", "admin_ally", "supervisor"]:
                    response["Head"]["ResponseCode"] = 200
                    response["Head"]["Description"] = "success"
                    response["Body"] = {
                        "is_account_active": "Active"
                    }
                    return Response(data=response)

                if cobrowse_agent_obj.is_active:
                    if not cobrowse_agent_obj.is_cobrowsing_active and not cobrowse_agent_obj.is_cognomeet_active:
                        response["Body"] = {
                            "is_active": "Available"
                        }
                    else:
                        response["Body"] = {
                            "is_active": "Busy"
                        }
                else:
                    response["Body"] = {
                        "is_account_active": "Offline"
                    }
            else:
                response["Body"] = {
                    "is_account_active": "Inactive"
                }

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMUserStatus = CRMUserStatusAPI.as_view()


class CRMAllUsersStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            active_agent = crm_integration_model.agent

            if active_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMAllUsersStatusAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            is_all_data_available = True
            required_inputs = ["user_email"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            agent_email = request_data["user_email"]
            agent_email = remo_special_tag_from_string(
                remo_html_from_string(agent_email)).strip()

            if not is_email_valid(agent_email):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Please enter valid user email."
                return Response(data=response)

            is_under_me = False
            if active_agent.role == "supervisor":
                if active_agent.user.username.lower() == agent_email:
                    is_under_me = True
            elif active_agent.role == "admin_ally":
                if active_agent.user.username.lower() == agent_email:
                    is_under_me = True

                if active_agent.agents.filter(role="supervisor", user__username__iexact=agent_email).count():
                    is_under_me = True
            else:
                is_under_me = is_agent_under_admin(
                    active_agent, agent_email, CobrowseAgent)

            if not is_under_me:
                response["Head"]["ResponseCode"] = 303
                response["Head"]["Description"] = "Unauthorized access"
                return Response(data=response)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_email).first()

            if cobrowse_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            agents = cobrowse_agent.agents.filter(role="agent")
            supervisors = cobrowse_agent.agents.filter(role="supervisor")
            admin_allies = cobrowse_agent.agents.filter(role="admin_ally")

            for admin_ally in admin_allies:
                ally_supervisors = admin_ally.agents.filter(role="supervisor")
                supervisors = supervisors | ally_supervisors
            for supervisor in supervisors:
                agents = agents | supervisor.agents.all()

            agents = agents.distinct()

            online_agents = agents.filter(is_active=True)
            offline_agents = agents.filter(is_active=False)
            active_agent_accounts = agents.filter(
                is_account_active=True)
            inactive_agent_accounts = agents.filter(
                is_account_active=False)
            available_agents = agents.filter(
                is_active=True, is_cobrowsing_active=False, is_cognomeet_active=False)
            busy_agents = online_agents.filter(
                ~Q(is_active=True, is_cobrowsing_active=False, is_cognomeet_active=False))

            online_agent_count = online_agents.count()
            offline_agent_count = offline_agents.count()
            active_agent_account_count = active_agent_accounts.count()
            available_agents_count = available_agents.count()
            inactive_agent_account_count = inactive_agent_accounts.count()
            busy_agents_count = busy_agents.count()

            online_agents_list = online_agents.values_list(
                'user__username', flat=True)
            offline_agents_list = offline_agents.values_list(
                'user__username', flat=True)
            active_agent_accounts_list = active_agent_accounts.values_list(
                'user__username', flat=True)
            available_agents_list = available_agents.values_list(
                'user__username', flat=True)
            inactive_agent_accounts_list = inactive_agent_accounts.values_list(
                'user__username', flat=True)
            busy_agents_list = busy_agents.values_list(
                'user__username', flat=True)

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "success"
            response["Body"] = {
                "online": online_agent_count,
                "online_agents": online_agents_list,
                "offline": offline_agent_count,
                "offline_agents": offline_agents_list,
                "active": active_agent_account_count,
                "active_agents": active_agent_accounts_list,
                "available": available_agents_count,
                "available_agents": available_agents_list,
                "inactive": inactive_agent_account_count,
                "inactive_agents": inactive_agent_accounts_list,
                "busy": busy_agents_count,
                "busy_agents": busy_agents_list,
            }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAllAgentsStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAllUsersStatus = CRMAllUsersStatusAPI.as_view()


class CRMGetListOfUsersAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            active_agent = crm_integration_model.agent

            if active_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMGetListOfUsersAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            is_all_data_available = True
            required_inputs = ["user_email"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            agent_email = request_data["user_email"]
            agent_email = remo_special_tag_from_string(
                remo_html_from_string(agent_email)).strip()

            if not is_email_valid(agent_email):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Please enter valid user email."
                return Response(data=response)

            is_under_me = False
            if active_agent.role == "supervisor":
                if active_agent.user.username.lower() == agent_email:
                    is_under_me = True
            elif active_agent.role == "admin_ally":
                if active_agent.user.username.lower() == agent_email:
                    is_under_me = True

                if active_agent.agents.filter(role="supervisor", user__username__iexact=agent_email).count():
                    is_under_me = True
            else:
                is_under_me = is_agent_under_admin(
                    active_agent, agent_email, CobrowseAgent)

            if not is_under_me:
                response["Head"]["ResponseCode"] = 303
                response["Head"]["Description"] = "Unauthorized access"
                return Response(data=response)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_email).first()

            if cobrowse_agent.role == "agent":
                response["Head"]["ResponseCode"] = 402
                response["Head"]["Description"] = "This API is unauthorized for agents"
                return Response(data=response)

            agents = cobrowse_agent.agents.filter(role="agent")

            if cobrowse_agent.role in ["admin", "admin_ally"]:
                supervisors = cobrowse_agent.agents.filter(role="supervisor")
                if cobrowse_agent.role == "admin":
                    admin_allies = cobrowse_agent.agents.filter(
                        role="admin_ally")
                    for admin_ally in admin_allies:
                        ally_supervisors = admin_ally.agents.filter(
                            role="supervisor")
                        supervisors = supervisors | ally_supervisors

                for supervisor in supervisors:
                    agents = agents | supervisor.agents.filter(role="agent")

                supervisors = supervisors.distinct()

            agents = agents.distinct()
            response_body = {}

            if cobrowse_agent.role == "admin":
                response_body = {
                    "agents": [agent.user.username for agent in agents],
                    "supervisors": [supervisor.user.username for supervisor in supervisors],
                    "admin_allies": [admin_ally.user.username for admin_ally in admin_allies],
                }
            elif cobrowse_agent.role == "admin_ally":
                response_body = {
                    "agents": [agent.user.username for agent in agents],
                    "supervisors": [supervisor.user.username for supervisor in supervisors],
                }
            elif cobrowse_agent.role == "supervisor":
                response_body = {
                    "agents": [agent.user.username for agent in agents],
                }

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "success"
            response["Body"] = response_body
            return Response(data=response)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGetListOfAgentsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMGetListOfUsers = CRMGetListOfUsersAPI.as_view()


class CRMChangeUserPasswordAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]["Description"] = "Unauthorized"
                return Response(data=response)

            active_agent = crm_integration_model.agent

            try:
                request_data = request.data
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMChangeUserPasswordAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["Head"]["ResponseCode"] = 400
                response["Head"]["Description"] = "Please send the request in valid JSON format."
                return Response(data=response)

            is_all_data_available = True
            required_inputs = ["user_email", "old_password", "new_password"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False
                    break

            if not is_all_data_available:
                response["Head"]["ResponseCode"] = 301
                response["Head"]["Description"] = "Required data is not present."
                return Response(data=response)

            agent_email = request_data["user_email"]
            agent_email = remo_special_tag_from_string(
                remo_html_from_string(agent_email)).strip()

            if not is_email_valid(agent_email):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Please enter valid user email."
                return Response(data=response)

            is_under_me = is_user_under_me(
                active_agent, agent_email, CobrowseAgent)

            if not is_under_me:
                if active_agent.role == "agent" and active_agent.user.username.lower() == agent_email.lower():
                    is_under_me = True

            if not is_under_me:
                response["Head"]["ResponseCode"] = 303
                response["Head"]["Description"] = "Unauthorized access"
                return Response(data=response)

            old_password = remo_special_tag_from_string(
                remo_html_from_string(request_data["old_password"]))
            new_password = request_data["new_password"]

            if not len(old_password) or not len(new_password):
                if not len(old_password) and not len(new_password):
                    response["Head"]["ResponseCode"] = 305
                    response["Head"]["Description"] = "Please enter old password and new password."
                    return Response(data=response)

                if not len(old_password):
                    response["Head"]["ResponseCode"] = 305
                    response["Head"]["Description"] = "Please enter old password."
                    return Response(data=response)

                if not len(new_password):
                    response["Head"]["ResponseCode"] = 305
                    response["Head"]["Description"] = "Please enter new password."
                    return Response(data=response)

            if not is_password_valid(new_password):
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Invalid new password. Password must not contain spaces. Minimum length of password should be 8 and must contain atleast a lowercase, an uppercase, a numerical and a special character from !, @, #, $, &, *"
                return Response(data=response)

            new_password = remo_special_tag_from_string(
                remo_html_from_string(new_password))
            agent_name = agent_email.split("@")[0]

            if agent_name in new_password:
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Your new password is too similar to your username please use strong password."
                return Response(data=response)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_email).first()
            user_obj = cobrowse_agent.user

            is_valid_password = True
            is_password_changed = False
            if old_password != "":
                if not user_obj.check_password(old_password):
                    is_valid_password = False
                else:
                    is_password_changed = True

            if is_valid_password:
                if is_password_changed:
                    update_resend_password_counter(cobrowse_agent)
                    if cobrowse_agent.resend_password_count >= 0:
                        if(validate_user_new_password(cobrowse_agent, new_password, old_password, AgentPasswordHistory) == "VALID"):
                            user_obj.is_online = False
                            user_obj.set_password(new_password)
                            user_obj.save()

                            new_password_hash = hashlib.sha256(
                                new_password.encode()).hexdigest()
                            AgentPasswordHistory.objects.create(
                                agent=cobrowse_agent, password_hash=new_password_hash)

                            description = "User (" + user_obj.first_name + \
                                "'s) password was changed"
                            save_audit_trail(cobrowse_agent, COBROWSING_UPDATEUSER_ACTION,
                                             description, CobrowsingAuditTrail)

                            add_audit_trail(
                                "EASYASSISTAPP",
                                user_obj,
                                "Updated-User",
                                description,
                                json.dumps({}),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )

                            response["Head"]["ResponseCode"] = 200
                            response["Head"]["Description"] = "success"
                        else:
                            response["Head"]["ResponseCode"] = 302
                            response["Head"]["Description"] = "Password matched with previous password"
                    else:
                        response["Head"]["ResponseCode"] = 307
                        response["Head"]["Description"] = str(
                            cobrowse_agent.user.email) + " has reached daily change password limit"
            else:
                response["Head"]["ResponseCode"] = 302
                response["Head"]["Description"] = "Your old password is incorrect. Kindly enter valid password."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentChangePasswordAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMChangeUserPassword = CRMChangeUserPasswordAPI.as_view()


class CRMUserGenerateAuthTokenAPI(APIView):

    authentication_classes = [BasicAuthentication]

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            username = request.user.username
            cobrowse_agent = CobrowseAgent.objects.get(user__username=username)
            access_token = cobrowse_agent.get_access_token_obj()

            crm_integration_model = CRMIntegrationModel.objects.create(
                access_token=access_token, agent=cobrowse_agent)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['auth_token'] = str(
                crm_integration_model.auth_token)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMUserGenerateAuthTokenAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMUserGenerateAuthToken = CRMUserGenerateAuthTokenAPI.as_view()
