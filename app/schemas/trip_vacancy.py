from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.schemas.common import MessageResponse  # noqa: F401
from app.schemas.profile import CountryResponse, CityResponse


# ============= Request Schemas =============
class TripVacancyCreateRequest(BaseModel):
    destination_country_id: int
    destination_city_id: int
    start_date: date
    end_date: date
    min_budget: Optional[Decimal] = Field(None, ge=0)
    max_budget: Optional[Decimal] = Field(None, ge=0)
    people_needed: int = Field(..., ge=1)
    description: Optional[str] = None
    planned_activities: Optional[str] = None
    planned_destinations: Optional[str] = None
    transportation_preference: Optional[str] = Field(None, max_length=50)
    accommodation_preference: Optional[str] = Field(None, max_length=50)
    min_age: Optional[int] = Field(None, ge=0, le=120)
    max_age: Optional[int] = Field(None, ge=0, le=120)
    gender_preference: Optional[str] = Field(None, max_length=20)


class TripVacancyUpdateRequest(BaseModel):
    destination_country_id: Optional[int] = None
    destination_city_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_budget: Optional[Decimal] = Field(None, ge=0)
    max_budget: Optional[Decimal] = Field(None, ge=0)
    people_needed: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    planned_activities: Optional[str] = None
    planned_destinations: Optional[str] = None
    transportation_preference: Optional[str] = Field(None, max_length=50)
    accommodation_preference: Optional[str] = Field(None, max_length=50)
    min_age: Optional[int] = Field(None, ge=0, le=120)
    max_age: Optional[int] = Field(None, ge=0, le=120)
    gender_preference: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)


# ============= Response Schemas =============
class TripVacancyResponse(BaseModel):
    id: int
    requester_id: int
    destination_country_id: int
    destination_city_id: int
    destination_country: Optional[CountryResponse] = None
    destination_city: Optional[CityResponse] = None
    start_date: date
    end_date: date
    min_budget: Optional[Decimal] = None
    max_budget: Optional[Decimal] = None
    people_needed: int
    people_joined: int
    description: Optional[str] = None
    planned_activities: Optional[str] = None
    planned_destinations: Optional[str] = None
    transportation_preference: Optional[str] = None
    accommodation_preference: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender_preference: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeneratePlanResponse(BaseModel):
    response: Dict[str, Any]
    
    class Config:
        from_attributes = True
