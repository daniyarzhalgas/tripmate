from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # Required Fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)

    # Location Fields
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    nationality = Column(String(100), nullable=True)

    # Contact Fields
    phone = Column(String(20), nullable=True)
    instagram_handle = Column(String(100), nullable=True)
    telegram_handle = Column(String(100), nullable=True)

    # Profile Details
    bio = Column(Text, nullable=True)
    profile_photo_url = Column(Text, nullable=True)
    travel_style = Column(
        String(50), nullable=True
    )  # e.g., "Budget", "Luxury", "Adventure"

    # Relationships
    user = relationship("User", back_populates="profile")
    languages = relationship(
        "UserLanguage", back_populates="profile", cascade="all, delete-orphan"
    )
    interests = relationship(
        "UserInterest", back_populates="profile", cascade="all, delete-orphan"
    )
