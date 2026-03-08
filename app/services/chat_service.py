from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_group import ChatGroup
from app.models.chat_member import ChatMember
from app.models.message import Message
from app.repositories.chat_group_repository import ChatGroupRepository
from app.repositories.chat_member_repository import ChatMemberRepository
from app.repositories.message_repository import MessageRepository


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_group_repo = ChatGroupRepository(db)
        self.chat_member_repo = ChatMemberRepository(db)
        self.message_repo = MessageRepository(db)

    # ============= CHAT GROUP OPERATIONS =============
    async def create_chat_group(
        self, trip_vacancy_id: int, name: str, owner_id: int
    ) -> Tuple[bool, Optional[ChatGroup], Optional[str]]:
        """Create a new chat group for a trip vacancy and add the owner as the first member."""
        try:
            # Check if chat group already exists for this trip vacancy
            existing_group = await self.chat_group_repo.get_by_trip_vacancy_id(
                trip_vacancy_id
            )
            if existing_group:
                return False, None, "Chat group already exists for this trip vacancy"

            # Create the chat group
            chat_group = await self.chat_group_repo.create(trip_vacancy_id, name)

            # Add the owner as the first member
            await self.chat_member_repo.create(chat_group.id, owner_id)

            return True, chat_group, None

        except Exception as e:
            return False, None, f"Failed to create chat group: {str(e)}"

    async def get_chat_group(
        self, chat_group_id: int, user_id: int
    ) -> Tuple[bool, Optional[ChatGroup], Optional[str]]:
        """Get chat group by ID. User must be a member."""
        try:
            chat_group = await self.chat_group_repo.get_by_id(chat_group_id)
            if not chat_group:
                return False, None, "Chat group not found"

            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group_id, user_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            return True, chat_group, None

        except Exception as e:
            return False, None, f"Failed to get chat group: {str(e)}"

    async def get_chat_group_by_trip_vacancy(
        self, trip_vacancy_id: int, user_id: int
    ) -> Tuple[bool, Optional[ChatGroup], Optional[str]]:
        """Get chat group for a trip vacancy. User must be a member."""
        try:
            chat_group = await self.chat_group_repo.get_by_trip_vacancy_id(
                trip_vacancy_id
            )
            if not chat_group:
                return False, None, "Chat group not found for this trip vacancy"

            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group.id, user_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            return True, chat_group, None

        except Exception as e:
            return False, None, f"Failed to get chat group: {str(e)}"

    async def get_my_chat_groups(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatGroup]:
        """Get all chat groups the user is a member of."""
        return await self.chat_group_repo.get_user_chat_groups(user_id, skip, limit)

    # ============= CHAT MEMBER OPERATIONS =============
    async def add_member(
        self, chat_group_id: int, user_id: int
    ) -> Tuple[bool, Optional[ChatMember], Optional[str]]:
        """Add a user to a chat group."""
        try:
            # Check if chat group exists
            chat_group = await self.chat_group_repo.get_by_id(chat_group_id)
            if not chat_group:
                return False, None, "Chat group not found"

            # Check if user is already a member
            existing_member = await self.chat_member_repo.get_by_chat_and_user(
                chat_group_id, user_id
            )
            if existing_member:
                return False, None, "User is already a member of this chat group"

            # Add the member
            member = await self.chat_member_repo.create(chat_group_id, user_id)
            return True, member, None

        except Exception as e:
            return False, None, f"Failed to add member: {str(e)}"

    async def get_chat_members(
        self, chat_group_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[bool, Optional[List[ChatMember]], Optional[str]]:
        """Get all members of a chat group. User must be a member."""
        try:
            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group_id, user_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            members = await self.chat_member_repo.get_members_by_chat_group(
                chat_group_id, skip, limit
            )
            return True, members, None

        except Exception as e:
            return False, None, f"Failed to get chat members: {str(e)}"

    async def remove_member(
        self, chat_group_id: int, user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Remove a user from a chat group."""
        try:
            # Check if user is a member
            member = await self.chat_member_repo.get_by_chat_and_user(
                chat_group_id, user_id
            )
            if not member:
                return False, "User is not a member of this chat group"

            await self.chat_member_repo.delete(member)
            return True, None

        except Exception as e:
            return False, f"Failed to remove member: {str(e)}"

    # ============= MESSAGE OPERATIONS =============
    async def send_message(
        self, chat_group_id: int, sender_id: int, content: str
    ) -> Tuple[bool, Optional[Message], Optional[str]]:
        """Send a message to a chat group. User must be a member."""
        try:
            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group_id, sender_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            # Create the message
            message = await self.message_repo.create(chat_group_id, sender_id, content)
            return True, message, None

        except Exception as e:
            return False, None, f"Failed to send message: {str(e)}"

    async def get_messages(
        self, chat_group_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[bool, Optional[List[Message]], Optional[str]]:
        """Get messages from a chat group. User must be a member."""
        try:
            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group_id, user_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            messages = await self.message_repo.get_messages_by_chat_group(
                chat_group_id, skip, limit
            )
            return True, messages, None

        except Exception as e:
            return False, None, f"Failed to get messages: {str(e)}"

    async def get_recent_messages(
        self, chat_group_id: int, user_id: int, limit: int = 50
    ) -> Tuple[bool, Optional[List[Message]], Optional[str]]:
        """Get recent messages from a chat group. User must be a member."""
        try:
            # Check if user is a member
            is_member = await self.chat_member_repo.is_member(chat_group_id, user_id)
            if not is_member:
                return False, None, "You are not a member of this chat group"

            messages = await self.message_repo.get_recent_messages(chat_group_id, limit)
            return True, messages, None

        except Exception as e:
            return False, None, f"Failed to get recent messages: {str(e)}"

    async def delete_message(
        self, message_id: int, user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Delete a message. Only the sender can delete their own message."""
        try:
            message = await self.message_repo.get_by_id(message_id)
            if not message:
                return False, "Message not found"

            # Check if user is the sender
            if message.sender_id != user_id:
                return False, "You can only delete your own messages"

            await self.message_repo.delete(message)
            return True, None

        except Exception as e:
            return False, f"Failed to delete message: {str(e)}"
