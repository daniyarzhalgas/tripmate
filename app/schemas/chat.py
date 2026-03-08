from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============= Request Schemas =============
class MessageSendRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


# ============= Response Schemas =============
class ChatGroupResponse(BaseModel):
    id: int
    trip_vacancy_id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMemberResponse(BaseModel):
    id: int
    chat_group_id: int
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    chat_group_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApiMessageResponse(BaseModel):
    message: str
