from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    room_name: str
    room_group_name: str

    def get_token_from_headers(self, headers):
        """Извлекаем токен из заголовка Authorization."""

        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return auth_header.split("Bearer ")[1]
        return None

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        headers = dict(self.scope.get("headers", []))
        token = self.get_token_from_headers(headers)
        self.scope["user"] = await self.get_user_from_token(token)

        if self.scope["user"] is None:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if self.scope["user"] is None:
            await self.close(code=4001)
            return

        message = content.get("message", "").strip()
        username = self.scope["user"].username

        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "username": username,
                    "sender_channel_name": self.channel_name,
                },
            )

    async def chat_message(self, event):
        if event.get("sender_channel_name") == self.channel_name:
            return

        await self.send_json(
            {
                "message": event["message"],
                "username": event["username"],
            }
        )

    async def get_user_from_token(self, token):
        """Получаем пользователя из токена."""

        from django.contrib.auth import get_user_model  # noqa WPS433
        from rest_framework_simplejwt.tokens import AccessToken  # noqa WPS433

        User = get_user_model()

        try:
            access_token = AccessToken(token)
            return await database_sync_to_async(User.objects.get)(id=access_token["user_id"])
        except Exception:
            return None
