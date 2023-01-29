from functools import reduce
from EasyAssistApp.utils import *


def is_supervisor_list_valid(supervisor_list, validation_response, active_agent):
    try:
        if not len(supervisor_list):
            validation_response["ValidatorResult"]["supervisor_list"] = "Supervisor list cannot be empty"
            return False

        for supervisor_name in supervisor_list:
            supervisor_name = sanitize_input_string(
                supervisor_name).strip()
            supervisor_obj = active_agent.agents.filter(
                user__username__iexact=supervisor_name, role="supervisor").first()

            if not supervisor_obj:
                validation_response["ValidatorResult"]["supervisor_list"] = "Supervisor object not found"
                return False

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_supervisor_list_valid %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return False


def is_language_list_valid(language_list, validation_response, active_agent):
    try:
        language_list = set(language_list)
        if not len(language_list):
            return True

        language_titles = map(lambda language_title: Q(
            title__iexact=language_title), language_list)
        language_titles = reduce(lambda a, b: a | b, language_titles)
        active_languages = active_agent.supported_language.filter(
            language_titles, is_deleted=False)

        if active_languages.count() == len(language_list):
            return True
        else:
            validation_response["ValidatorResult"]["language_list"] = "Some of the languages are not supported by the agent"
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_language_list_valid %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return False


def is_product_category_list_valid(product_category_list, validation_response, active_agent):
    try:
        product_category_list = set(product_category_list)
        if not len(product_category_list):
            return True

        product_category_titles = map(lambda product_category_title: Q(
            title__iexact=product_category_title), product_category_list)
        product_category_titles = reduce(
            lambda a, b: a | b, product_category_titles)
        active_product_categories = active_agent.product_category.filter(
            product_category_titles, is_deleted=False)

        if active_product_categories.count() == len(product_category_list):
            return True
        else:
            validation_response["ValidatorResult"]["product_category_list"] = "Some of the product categories are not supported by the agent"
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_product_category_list_valid %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return False


def is_user_under_me(active_agent, agent_email, CobrowseAgent):
    try:
        is_under_me = False
        if active_agent.role == "admin":
            is_under_me = is_agent_under_admin(
                active_agent, agent_email, CobrowseAgent)
        elif active_agent.role == "admin_ally":
            if active_agent.user.username.lower() == agent_email.lower():
                is_under_me = True

            if not is_under_me:
                supervisors = active_agent.agents.filter(role="supervisor")

                for supervisor in supervisors:
                    if supervisor.user.username.lower() == agent_email.lower():
                        is_under_me = True

                    if supervisor.agents.filter(user__username__iexact=agent_email).count():
                        is_under_me = True

                    if is_under_me:
                        break
        elif active_agent.role == "supervisor":
            if active_agent.user.username.lower() == agent_email.lower():
                is_under_me = True

            if not is_under_me:
                if active_agent.agents.filter(user__username__iexact=agent_email).count():
                    is_under_me = True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_user_under_me %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return is_under_me
