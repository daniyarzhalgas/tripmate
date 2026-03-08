from typing import Dict, List, Set
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections for chat groups."""

    def __init__(self):
        # Dictionary mapping chat_group_id to set of active WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Dictionary mapping WebSocket to user_id for authentication
        self.connection_users: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, chat_group_id: int, user_id: int):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Add to active connections for this chat group
        if chat_group_id not in self.active_connections:
            self.active_connections[chat_group_id] = set()

        self.active_connections[chat_group_id].add(websocket)
        self.connection_users[websocket] = user_id

        # Send connection confirmation
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "chat_group_id": chat_group_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def disconnect(self, websocket: WebSocket, chat_group_id: int):
        """Remove a WebSocket connection."""
        if chat_group_id in self.active_connections:
            self.active_connections[chat_group_id].discard(websocket)

            # Clean up empty chat groups
            if not self.active_connections[chat_group_id]:
                del self.active_connections[chat_group_id]

        # Remove from connection_users mapping
        if websocket in self.connection_users:
            del self.connection_users[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        await websocket.send_json(message)

    async def broadcast_to_chat_group(
        self, chat_group_id: int, message: dict, exclude: WebSocket = None
    ):
        """Broadcast a message to all connections in a chat group, optionally excluding one."""
        if chat_group_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[chat_group_id]:
            if connection == exclude:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                # Connection is broken, mark for removal
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, chat_group_id)

    async def send_typing_indicator(
        self, chat_group_id: int, user_id: int, is_typing: bool
    ):
        """Broadcast typing indicator to all members in chat group."""
        message = {
            "type": "typing",
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_chat_group(chat_group_id, message)

    def get_active_users(self, chat_group_id: int) -> List[int]:
        """Get list of active user IDs in a chat group."""
        if chat_group_id not in self.active_connections:
            return []

        user_ids = set()
        for connection in self.active_connections[chat_group_id]:
            if connection in self.connection_users:
                user_ids.add(self.connection_users[connection])

        return list(user_ids)


# Global connection manager instance
manager = ConnectionManager()
