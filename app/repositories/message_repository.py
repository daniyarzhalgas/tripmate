from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= CREATE =============
    async def create(self, chat_group_id: int, sender_id: int, content: str) -> Message:
        """Create a new message."""
        message = Message(
            chat_group_id=chat_group_id, sender_id=sender_id, content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    # ============= READ =============
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        query = select(Message).filter(Message.id == message_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_messages_by_chat_group(
        self, chat_group_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """Get all messages in a chat group."""
        query = (
            select(Message)
            .filter(Message.chat_group_id == chat_group_id)
            .options(selectinload(Message.sender))
            .offset(skip)
            .limit(limit)
            .order_by(Message.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_messages(
        self, chat_group_id: int, limit: int = 50
    ) -> List[Message]:
        """Get recent messages from a chat group."""
        query = (
            select(Message)
            .filter(Message.chat_group_id == chat_group_id)
            .options(selectinload(Message.sender))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        # Reverse to get chronological order
        return list(reversed(list(result.scalars().all())))

    # ============= UPDATE =============
    async def update(self, message: Message, **kwargs) -> Message:
        """Update a message."""
        for key, value in kwargs.items():
            if hasattr(message, key):
                setattr(message, key, value)

        await self.db.commit()
        await self.db.refresh(message)
        return message

    # ============= DELETE =============
    async def delete(self, message: Message) -> None:
        """Delete a message."""
        await self.db.delete(message)
        await self.db.commit()
