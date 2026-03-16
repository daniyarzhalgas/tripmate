from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RecommendedPlaceResponse(BaseModel):
    id: int
    place_id: str
    name: str
    category: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    short_description: Optional[str] = None
    why_people_go: Optional[str] = None
    why_recommended: Optional[str] = None
    highlights: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    best_season: Optional[List[str]] = None
    audience: Optional[List[str]] = None
    estimated_cost: Optional[Decimal] = None
    ticket_price: Optional[Decimal] = None
    visit_duration_minutes: Optional[int] = None
    best_time_of_day: Optional[str] = None
    rating: Optional[Decimal] = None
    reviews_count: Optional[int] = None
    image_url: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    contact_information: Optional[Dict[str, Any]] = None
    age_range: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TripPlanResponse(BaseModel):
    id: int
    trip_vacancy_id: int
    generation_requested_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    recommended_places: List[RecommendedPlaceResponse]

    class Config:
        from_attributes = True