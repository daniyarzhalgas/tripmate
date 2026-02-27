
from datetime import date
from decimal import Decimal

from sqlalchemy import Numeric, Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TripVacancy(Base):
    __tablename__ = "trip_vacancies"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Destination Fields
    destination_city = Column(String(100), nullable=False)
    destination_country = Column(String(100), nullable=False)

    # Date Fields
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Budget Fields
    min_budget = Column(Numeric(precision=10, scale=2), nullable=True)
    max_budget = Column(Numeric(precision=10, scale=2), nullable=True)

    # Trip Details
    people_needed = Column(Integer, nullable=False)
    people_joined = Column(Integer, default=0, nullable=False)
    
    description = Column(Text, nullable=True)
    planned_activities = Column(
        Text, nullable=True
    )  # e.g., "Hiking, Sightseeing, Food tours"
    planned_destinations = Column(
        Text, nullable=True
    )  # e.g., "Eiffel Tower, Louvre Museum"
    transportation_preference = Column(
        String(50), nullable=True
    )  # e.g., "Plane", "Train", "Car"
    accommodation_preference = Column(
        String(50), nullable=True
    )  # e.g., "Hotel", "Hostel", "Airbnb"

    # Preference Filters
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    gender_preference = Column(
        String(20), nullable=True
    )  # e.g., "Male", "Female", "Any"

    # Status
    status = Column(
        String(20), default="open", nullable=False
    )  # open, matched, closed, cancelled

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    offers = relationship("Offer", back_populates="vacancy", cascade="all, delete-orphan")

    
    @property
    def is_accepting_offers(self) -> bool:
        return (
            self.status == "active" and 
            self.people_joined < self.people_needed and
            self.end_date >= date.today()
        )

    # Relationships
    requester = relationship("User", back_populates="trip_vacancies")
