import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Tour, Location, ChatMessage, Notification


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tour_id = self.scope['url_route']['kwargs']['tour_id']
        self.room_group_name = f'location_{self.tour_id}'

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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'location_update':
            latitude = text_data_json['latitude']
            longitude = text_data_json['longitude']
            accuracy = text_data_json.get('accuracy')

            # Save location to database
            await self.save_location(self.tour_id, latitude, longitude, accuracy)

            # Send location to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_message',
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy,
                    'timestamp': text_data_json.get('timestamp')
                }
            )

    async def location_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event['accuracy'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_location(self, tour_id, latitude, longitude, accuracy):
        try:
            tour = Tour.objects.get(id=tour_id)
            Location.objects.create(
                tour=tour,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy
            )
        except Tour.DoesNotExist:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'

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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'mark_read':
            notification_id = text_data_json['notification_id']
            await self.mark_notification_read(notification_id)

    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tour_id = self.scope['url_route']['kwargs']['tour_id']
        self.room_group_name = f'chat_{self.tour_id}'

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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json['user_id']

        # Save message to database
        message_obj = await self.save_message(self.tour_id, user_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'username': message_obj['username'],
                'timestamp': message_obj['timestamp']
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, tour_id, user_id, message):
        try:
            tour = Tour.objects.get(id=tour_id)
            user = User.objects.get(id=user_id)
            
            chat_message = ChatMessage.objects.create(
                tour=tour,
                sender=user,
                message=message
            )
            
            return {
                'username': user.username,
                'timestamp': chat_message.timestamp.isoformat()
            }
        except (Tour.DoesNotExist, User.DoesNotExist):
            return {
                'username': 'Unknown',
                'timestamp': ''
            }
