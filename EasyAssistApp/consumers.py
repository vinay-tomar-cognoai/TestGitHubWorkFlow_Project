from channels.generic.websocket import AsyncWebsocketConsumer
from EasyAssistApp.encrypt import CustomEncrypt
from EasyAssistApp.models import CobrowseIO
from django.utils import timezone

import json
import logging

logger = logging.getLogger(__name__)


class CobrowsingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.custom_encrypt_obj = CustomEncrypt()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        """
        cobrowse_io_obj = None
        is_session_closed = False
        try:
            cobrowse_io_obj = CobrowseIO.objects.get(session_id=self.room_name)
        except Exception:
            is_session_closed = True

        if cobrowse_io_obj==None:
            return

        header = message["header"]
        body = message["body"]

        sender = header["sender"]
        request_packet = self.custom_encrypt_obj.decrypt(body["Request"])
        request_packet = json.loads(request_packet)

        if sender=="client":

            if request_packet["type"]=="heartbeat" and (not cobrowse_io_obj.is_active_timer()):
                logger.info("Closing cobrowsing session due to inactivity...")
                is_session_closed = True
                cobrowse_io_obj.is_active = False

            if request_packet["type"]=="html":
                # cobrowse_io_obj.html = request_packet["html"]
                cobrowse_io_obj.html = "html"

            cobrowse_io_obj.active_url = request_packet["active_url"]
            cobrowse_io_obj.is_active = True
            cobrowse_io_obj.is_updated = True

            if request_packet["type"]!="heartbeat":
                cobrowse_io_obj.last_update_datetime = timezone.now()

            cobrowse_io_obj.save()

            agent_name = None
            if cobrowse_io_obj.agent != None:
                agent_name = str(cobrowse_io_obj.agent.user.username)

            request_packet["is_agent_connected"] = cobrowse_io_obj.is_agent_active_timer() and cobrowse_io_obj.is_agent_connected
            request_packet["agent_assistant_request_status"] = cobrowse_io_obj.agent_assistant_request_status

            if is_session_closed:
                request_packet["is_session_closed"] = True
            else:
                request_packet["is_session_closed"] = cobrowse_io_obj.is_closed_session

            request_packet["agent_name"] = agent_name
            request_packet["allow_agent_cobrowse"] = cobrowse_io_obj.allow_agent_cobrowse
            request_packet["is_lead"] = cobrowse_io_obj.is_lead
            request_packet["is_archived"] = cobrowse_io_obj.is_archived
            request_packet = self.custom_encrypt_obj.encrypt(json.dumps(request_packet))

            message = {
                "header":{
                    "sender": sender
                },
                "body":{
                    "Request": request_packet
                }
            }

        else:
            cobrowse_io_obj.last_agent_update_datetime = timezone.now()
            cobrowse_io_obj.is_agent_connected = True
            cobrowse_io_obj.save()

            if is_session_closed:
                request_packet["is_client_connected"] = False
            else:
                request_packet["is_client_connected"] = cobrowse_io_obj.is_active and cobrowse_io_obj.is_active_timer()

            request_packet = self.custom_encrypt_obj.encrypt(json.dumps(request_packet))

            message = {
                "header":{
                    "sender": sender
                },
                "body":{
                    "Request": request_packet
                }
            }
        """

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class SyncUtilsCobrowsingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.custom_encrypt_obj = CustomEncrypt()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class CobrowsingMeeting(AsyncWebsocketConsumer):

    async def connect(self):
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class CognoAIsignal(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.app_token = self.scope['url_route']['kwargs']['app_token']
        self.room_group_name = 'chat_%s' % self.app_token

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': json.dumps(message),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))
