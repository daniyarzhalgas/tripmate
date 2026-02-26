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


class TravelStyle(Base):
    __tablename__ = "travel_styles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fields
    name = Column(String(100), unique=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user_travel_styles = relationship("UserTravelStyle", back_populates="travel_style")


class UserTravelStyle(Base):
    __tablename__ = "user_travel_styles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))
    travel_style_id = Column(
        Integer, ForeignKey("travel_styles.id", ondelete="CASCADE")
    )

    # Relationships
    profile = relationship("Profile", back_populates="travel_styles")
    travel_style = relationship("TravelStyle", back_populates="user_travel_styles")

    __table_args__ = (
        UniqueConstraint(
            "profile_id", "travel_style_id", name="unique_user_travel_style"
        ),
        Index("idx_profile_travel_styles", "profile_id"),
        Index("idx_travel_style_profiles", "travel_style_id"),
    )
