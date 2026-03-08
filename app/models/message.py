from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    chat_group_id = Column(
        Integer, ForeignKey("chat_groups.id", ondelete="CASCADE"), nullable=False
    )
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message Content
    content = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    chat_group = relationship("ChatGroup", back_populates="messages")
    sender = relationship("User", back_populates="messages")
