from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Language(Base):
    __tablename__ = "languages"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(100), unique=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user_languages = relationship("UserLanguage", back_populates="language")


class UserLanguage(Base):
    __tablename__ = "user_languages"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    language_id = Column(Integer, ForeignKey("languages.id", ondelete="CASCADE"))

    # Relationships
    profile = relationship("Profile", back_populates="languages")
    language = relationship("Language", back_populates="user_languages")

    __table_args__ = (
        UniqueConstraint("profile_id", "language_id", name="unique_user_language"),
        Index("idx_profile_languages", "profile_id"),
        Index("idx_language_profiles", "language_id"),
    )
