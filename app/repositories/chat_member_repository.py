from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_member import ChatMember


class ChatMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= CREATE =============
    async def create(self, chat_group_id: int, user_id: int) -> ChatMember:
        """Create a new chat member."""
        chat_member = ChatMember(chat_group_id=chat_group_id, user_id=user_id)
        self.db.add(chat_member)
        await self.db.commit()
        await self.db.refresh(chat_member)
        return chat_member

    # ============= READ =============
    async def get_by_id(self, member_id: int) -> Optional[ChatMember]:
        """Get chat member by ID."""
        query = select(ChatMember).filter(ChatMember.id == member_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_chat_and_user(
        self, chat_group_id: int, user_id: int
    ) -> Optional[ChatMember]:
        """Check if a user is a member of a chat group."""
        query = select(ChatMember).filter(
            and_(
                ChatMember.chat_group_id == chat_group_id, ChatMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_members_by_chat_group(
        self, chat_group_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatMember]:
        """Get all members of a chat group."""
        query = (
            select(ChatMember)
            .filter(ChatMember.chat_group_id == chat_group_id)
            .options(selectinload(ChatMember.user))
            .offset(skip)
            .limit(limit)
            .order_by(ChatMember.joined_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def is_member(self, chat_group_id: int, user_id: int) -> bool:
        """Check if user is a member of the chat group."""
        member = await self.get_by_chat_and_user(chat_group_id, user_id)
        return member is not None

    # ============= DELETE =============
    async def delete(self, chat_member: ChatMember) -> None:
        """Remove a chat member."""
        await self.db.delete(chat_member)
        await self.db.commit()
