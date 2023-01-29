import os
import sys
import json
import logging
from os import path
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from LiveChatApp.models import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.constants import *
from LiveChatApp.utils import *
from LiveChatApp.constants_processors import LIVECHAT_PROCESSOR_EXAMPLE_PREVIOUS_TICKETS, LIVECHAT_PROCESSOR_EXAMPLE_SEARCH_TICKET, LIVECHAT_PROCESSOR_EXAMPLE_RAISE_TICKET 

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def RaiseTicketFormBuilder(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            bot_pk = request.GET["bot_pk"]

            if user_obj.status == "1":

                bot_obj = Bot.objects.get(pk=int(bot_pk))
                form_obj = LiveChatRaiseTicketForm.objects.filter(bot=bot_obj)

                if not form_obj:
                    form_obj = LiveChatRaiseTicketForm.objects.create(
                        bot=bot_obj, form=json.dumps({}))
                else:
                    form_obj = form_obj[0]

                is_form_enabled = form_obj.is_form_enabled
                form = form_obj.form

                category_list = []
                category_objs = admin_config.admin.category.all().filter(
                    bot__pk=int(bot_pk), is_public=True, is_deleted=False)
                for item in category_objs:
                    category_list.append(str(item.title))

                return render(request, 'LiveChatApp/raise_ticket_form_builder.html', {'user_obj': user_obj, 'admin_config': admin_config, 'bot_pk': bot_pk, 'is_form_enabled': is_form_enabled, 'form': form, 'bot_obj': bot_obj, 'category_list': category_list})
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RaiseTicketFormBuilder: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class SaveRaiseTicketFormAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_pk"]
            is_form_enabled = data['is_form_enabled']
            form = data['form']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            form_obj = LiveChatRaiseTicketForm.objects.get(bot=bot_obj)

            form_obj.is_form_enabled = is_form_enabled

            if is_form_enabled:
                form_obj.form = json.dumps(form)

            form_obj.edited_datetime = timezone.now()
            form_obj.save()

            response["status"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveRaiseTicketFormAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveRaiseTicketForm = SaveRaiseTicketFormAPI.as_view()


class LiveChatRaiseTicketAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            ticket_id = ""
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            form_filled = data['form_filled']
            session_id = data['session_id']

            form_filled = clean_dynamic_form_data(form_filled)
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            livechat_agent_object = LiveChatUser.objects.get(user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            parameter = {}
            parameter["form_filled"] = form_filled
            parameter["livechat_agent_obj"] = livechat_agent_object
            parameter["customer_obj"] = customer_obj

            processor_check_dictionary = {'open': open_file}
            processor_obj = LiveChatProcessors.objects.filter(bot=customer_obj.bot)

            if processor_obj:
                processor_obj = processor_obj.first()

                if not processor_obj.raise_ticket_processor:

                    processor_obj.raise_ticket_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_RAISE_TICKET)
                    processor_obj.save()

                code = processor_obj.raise_ticket_processor.function
                exec(str(code), processor_check_dictionary)

                ticket_id = processor_check_dictionary['f'](parameter)

            if ticket_id:
                response["status"] = 200
                response["status_message"] = "Success"
                response["ticket_id"] = ticket_id
            
                LiveChatTicketAudit.objects.create(customer=customer_obj, agent=livechat_agent_object, ticket_id=ticket_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatRaiseTicketAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatRaiseTicket = LiveChatRaiseTicketAPI.as_view()    


class LiveChatSearchTicketAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            ticket_id = data['ticket_id']
            session_id = data['session_id']

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            livechat_agent_object = LiveChatUser.objects.get(user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            parameter = {}
            parameter["ticket_id"] = ticket_id
            parameter["livechat_agent_obj"] = livechat_agent_object

            processor_check_dictionary = {'open': open_file}
            processor_obj = LiveChatProcessors.objects.filter(bot=customer_obj.bot)

            if processor_obj:
                processor_obj = processor_obj.first()

                if not processor_obj.search_ticket_processor:

                    processor_obj.search_ticket_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_SEARCH_TICKET)
                    processor_obj.save()

                code = processor_obj.search_ticket_processor.function
                exec(str(code), processor_check_dictionary)

                ticket_search_response = processor_check_dictionary['f'](parameter)

                response["status"] = ticket_search_response['status_code']
                response["status_message"] = ticket_search_response['status_message']

                if ticket_search_response['status_code'] == 200:

                    response["ticket_info"] = ticket_search_response['ticket_info']

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatSearchTicketAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatSearchTicket = LiveChatSearchTicketAPI.as_view() 


class LiveChatGetPreviousTicketsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data['session_id']
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            parameter = {}
            parameter["customer_phone"] = customer_obj.phone_country_code + customer_obj.phone
            
            processor_check_dictionary = {'open': open_file}
            processor_obj = LiveChatProcessors.objects.filter(bot=customer_obj.bot)

            if processor_obj:
                processor_obj = processor_obj.first()

                if not processor_obj.get_previous_tickets_processor:

                    processor_obj.get_previous_tickets_processor = LiveChatDeveloperProcessor.objects.create(
                        function=LIVECHAT_PROCESSOR_EXAMPLE_PREVIOUS_TICKETS)
                    processor_obj.save()
    
                code = processor_obj.get_previous_tickets_processor.function
                exec(str(code), processor_check_dictionary)

                ticket_response = processor_check_dictionary['f'](parameter)

                response["status"] = ticket_response['status_code']
                response["status_message"] = ticket_response['status_message']

                if ticket_response['status_code'] == 200:

                    response["ticket_info_list"] = ticket_response['ticket_info_list']

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatGetPreviousTicketsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatGetPreviousTickets = LiveChatGetPreviousTicketsAPI.as_view()     
