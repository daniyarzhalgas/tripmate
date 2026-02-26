from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ============= Request Schemas =============
class TripVacancyCreateRequest(BaseModel):
    destination_city: str = Field(..., min_length=1, max_length=100)
    destination_country: str = Field(..., min_length=1, max_length=100)
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
    destination_city: Optional[str] = Field(None, min_length=1, max_length=100)
    destination_country: Optional[str] = Field(None, min_length=1, max_length=100)
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
    destination_city: str
    destination_country: str
    start_date: date
    end_date: date
    min_budget: Optional[Decimal] = None
    max_budget: Optional[Decimal] = None
    people_needed: int
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


class MessageResponse(BaseModel):
    message: str
