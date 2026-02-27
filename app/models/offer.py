import enum

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Text, func)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Offer(Base):
    __tablename__ = "offers"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    trip_vacancy_id = Column(
        Integer, ForeignKey("trip_vacancies.id", ondelete="CASCADE")
    )
    offerer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Offer Details
    message = Column(Text, nullable=True)
    proposed_budget = Column(Numeric(precision=10, scale=2), nullable=True)

    # Status
    status = Column(
        String(20), default="pending", nullable=False
    )  # pending, accepted, rejected

    # Metadata
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    vacancy = relationship("TripVacancy", back_populates="offers")
    offerer = relationship("User", back_populates="offers")
