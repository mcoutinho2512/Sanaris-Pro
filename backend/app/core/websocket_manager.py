from typing import Dict, Set
from fastapi import WebSocket
from uuid import UUID
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # user_id -> Set[WebSocket]
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        # channel_id -> Set[user_id]
        self.channel_subscribers: Dict[UUID, Set[UUID]] = {}
        # user_id -> channel_id (for typing indicators)
        self.typing_users: Dict[UUID, UUID] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Broadcast online status
        await self.broadcast_online_status(user_id, True)

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Broadcast offline status
                asyncio.create_task(self.broadcast_online_status(user_id, False))

    async def subscribe_to_channel(self, user_id: UUID, channel_id: UUID):
        if channel_id not in self.channel_subscribers:
            self.channel_subscribers[channel_id] = set()
        self.channel_subscribers[channel_id].add(user_id)

    async def unsubscribe_from_channel(self, user_id: UUID, channel_id: UUID):
        if channel_id in self.channel_subscribers:
            self.channel_subscribers[channel_id].discard(user_id)

    async def send_personal_message(self, message: dict, user_id: UUID):
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

    async def broadcast_to_channel(self, message: dict, channel_id: UUID, exclude_user: UUID = None):
        if channel_id in self.channel_subscribers:
            for user_id in self.channel_subscribers[channel_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                await self.send_personal_message(message, user_id)

    async def broadcast_typing_indicator(self, channel_id: UUID, user_id: UUID, user_name: str, is_typing: bool):
        message = {
            "type": "typing",
            "data": {
                "channel_id": str(channel_id),
                "user_id": str(user_id),
                "user_name": user_name,
                "is_typing": is_typing
            }
        }
        await self.broadcast_to_channel(message, channel_id, exclude_user=user_id)

    async def broadcast_online_status(self, user_id: UUID, is_online: bool):
        message = {
            "type": "online_status",
            "data": {
                "user_id": str(user_id),
                "is_online": is_online,
                "last_seen": datetime.utcnow().isoformat()
            }
        }
        # Broadcast to all connected users
        for connected_user_id in self.active_connections.keys():
            if connected_user_id != user_id:
                await self.send_personal_message(message, connected_user_id)

    async def broadcast_read_receipt(self, message_id: UUID, channel_id: UUID, user_id: UUID):
        message = {
            "type": "read_receipt",
            "data": {
                "message_id": str(message_id),
                "channel_id": str(channel_id),
                "user_id": str(user_id),
                "read_at": datetime.utcnow().isoformat()
            }
        }
        await self.broadcast_to_channel(message, channel_id)

# Global instance
manager = ConnectionManager()
