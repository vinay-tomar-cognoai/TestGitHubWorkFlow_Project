import sys
import pytz

from django.conf import settings

# Logger
import logging
logger = logging.getLogger(__name__)


def get_formatted_date(date_obj):
    data = None
    try:
        if date_obj:
            est = pytz.timezone(settings.TIME_ZONE)
            data = date_obj.astimezone(
                est).strftime("%d %b %Y %I:%M:%S %p")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_formatted_date %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return data


def get_agent_name(agent_obj):
    agent_name = ""

    try:
        if agent_obj and agent_obj.user:
            agent_name = agent_obj.user.first_name + ' ' + agent_obj.user.last_name
            agent_name = agent_name.strip()
            if agent_name == "":
                agent_name = agent_obj.user.username
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_agent_name %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

    return agent_name


def parse_ticket_category(ticket_category_obj):
    data = None
    try:
        if ticket_category_obj:
            data = {
                'pk': ticket_category_obj.pk,
                'ticket_category': ticket_category_obj.ticket_category,
                'is_deleted': ticket_category_obj.is_deleted,
                'ticket_period': ticket_category_obj.ticket_period,
                'created_datetime': get_formatted_date(ticket_category_obj.created_datetime),
                'bot': parse_bot(ticket_category_obj.bot)
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Agent parse_ticket_category error: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

    return data


def parse_bot(bot_obj):
    data = None
    try:
        if bot_obj:
            data = {
                'pk': bot_obj.pk,
                'name': bot_obj.name,
                'bot_display_name': bot_obj.bot_display_name,
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Agent parse_bot error: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

    return data


def parse_bot_channel(bot_channel_obj):
    data = None
    try:
        if bot_channel_obj:
            data = {
                'pk': bot_channel_obj.pk,
                'name': bot_channel_obj.name,
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_bot_channel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return data


def parse_customer_details(ticket_obj):
    customer_details = {}
    try:
        customer_details = {
            "customer_name": ticket_obj.customer_name,
            "customer_email_id": ticket_obj.customer_email_id,
            "customer_mobile_number": ticket_obj.customer_mobile_number
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_customer_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return customer_details


def parse_ticket_audit_trail_model(audit_trail_obj):
    audit_trail_data = {}
    try:
        audit_trail_data = {
            "ticket_id": audit_trail_obj.ticket.ticket_id,
            "agent_detail": parse_agent_details(audit_trail_obj.agent),
            "action_type": audit_trail_obj.action_type,
            "description": audit_trail_obj.description,
            "datetime": get_formatted_date(audit_trail_obj.datetime),
            "customer_details": parse_customer_details(audit_trail_obj.ticket),
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_ticket_audit_trail_model %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return audit_trail_data


def parse_agent_details(agent_obj):
    agent_detail = {}
    try:
        if agent_obj:
            agent_detail = {
                "pk": agent_obj.pk,
                "agent_username": agent_obj.user.username,
                "name": get_agent_name(agent_obj),
                "role": agent_obj.role,
                "level": agent_obj.level,
                "phone_number": agent_obj.phone_number,
                "is_absent": agent_obj.is_absent,
                "is_active": agent_obj.is_active,
                "is_account_active": agent_obj.is_account_active,
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_agent_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return agent_detail


def parse_user_notification(user_notification_obj):
    user_notification = {}
    try:
        user_notification = {
            "ticket_id": user_notification_obj.ticket.ticket_id,
            "pk": user_notification_obj.pk,
            "query_description": user_notification_obj.ticket.query_description,
            "agent_detail": parse_agent_details(user_notification_obj.agent),
            "description": user_notification_obj.description,
            "datetime": get_formatted_date(user_notification_obj.datetime),
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_user_notification %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return user_notification


def parse_agent_query_related_info(agent_query_obj):
    ticket_audit_trail_obj = agent_query_obj.ticket_audit_trail
    ticket_obj = ticket_audit_trail_obj.ticket
    """
    {
        "customer_info": {
            "customer_name": '',
            "customer_email_id": '',
            "customer_mobile_number": '',
        },
        "ticket_info": {
            "ticket_status": '',
            "ticket_priority": '',
            "ticket_id": '',
        },
        "query_info": {
            "datetime": "",
            "message": ""
        }
    }
    """
    def parse_customer_info():
        return {
            "customer_name": ticket_obj.customer_name,
            "customer_email_id": ticket_obj.customer_email_id,
            "customer_mobile_number": ticket_obj.customer_mobile_number,
        }

    def parse_ticket_info():
        return {
            "ticket_id": str(ticket_obj.ticket_id),
            "ticket_status": ticket_obj.ticket_status.name,
            "ticket_priority": ticket_obj.ticket_priority.name,
        }

    def parse_query_info():
        return {
            "datetime": get_formatted_date(ticket_audit_trail_obj.datetime),
            "message": ticket_audit_trail_obj.description
        }

    data = None
    try:
        data = {
            "customer_info": parse_customer_info(),
            "ticket_info": parse_ticket_info(),
            "query_info": parse_query_info(),
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_whatsapp_send_message_info %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return data
