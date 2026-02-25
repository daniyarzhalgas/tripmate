from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Interest(Base):
    __tablename__ = "interests"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(100), nullable=False)

    # Relationships
    user_interests = relationship("UserInterest", back_populates="interest")


class UserInterest(Base):
    __tablename__ = "user_interests"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"))

    # Relationships
    profile = relationship("Profile", back_populates="interests")
    interest = relationship("Interest", back_populates="user_interests")

    __table_args__ = (
        UniqueConstraint("profile_id", "interest_id", name="unique_user_interest"),
    )
