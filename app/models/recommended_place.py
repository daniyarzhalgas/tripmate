from sqlalchemy import (
    JSON,
    Numeric,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RecommendedPlace(Base):
    __tablename__ = "recommended_places"

    id = Column(Integer, primary_key=True, autoincrement=True)
    generated_plan_id = Column(
        Integer,
        ForeignKey("generated_trip_plans.id", ondelete="CASCADE"),
        nullable=False,
    )

    place_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)

    latitude = Column(Numeric(precision=10, scale=7), nullable=True)
    longitude = Column(Numeric(precision=10, scale=7), nullable=True)

    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    short_description = Column(Text, nullable=True)
    why_people_go = Column(Text, nullable=True)
    why_recommended = Column(Text, nullable=True)

    highlights = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    best_season = Column(JSON, nullable=True)
    audience = Column(JSON, nullable=True)

    estimated_cost = Column(Numeric(precision=10, scale=2), nullable=True)
    ticket_price = Column(Numeric(precision=10, scale=2), nullable=True)
    visit_duration_minutes = Column(Integer, nullable=True)

    best_time_of_day = Column(String(50), nullable=True)
    rating = Column(Numeric(precision=3, scale=2), nullable=True)
    reviews_count = Column(Integer, nullable=True)

    image_url = Column(String(1000), nullable=True)
    opening_hours = Column(JSON, nullable=True)
    contact_information = Column(JSON, nullable=True)
    age_range = Column(JSON, nullable=True)

    raw_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    query_to_search = Column(String(255), nullable=True)

    generated_plan = relationship(
        "GeneratedTripPlan", back_populates="recommended_places"
    )
