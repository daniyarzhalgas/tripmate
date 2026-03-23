from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CoordinatesSchema(BaseModel):
    latitude: float
    longitude: float


class OpeningHoursSchema(BaseModel):
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str
    notes: str  # no Optional, no default


class ContactInformationSchema(BaseModel):
    phone: str  # no Optional, no default
    website: str
    email: str


class AgeRangeSchema(BaseModel):
    min_age: int
    max_age: int


class RecommendedPlaceSchema(BaseModel):
    place_id: str
    name: str
    category: Literal[
        "landmark", "restaurant", "museum", "nature", "sports",
        "cultural", "shopping", "activity", "wellness",
    ]
    coordinates: CoordinatesSchema
    address: str
    city: str
    country: str
    short_description: str
    why_people_go: str
    why_recommended: str
    highlights: list[str]
    tags: list[str]
    estimated_cost: float
    ticket_price: float
    visit_duration_minutes: int
    best_time_of_day: Literal["morning", "afternoon", "evening", "sunset", "night"]
    best_season: list[Literal["spring", "summer", "autumn", "winter"]]
    rating: float
    reviews_count: int
    image_url: str
    opening_hours: OpeningHoursSchema
    contact_information: ContactInformationSchema
    age_range: AgeRangeSchema
    audience: list[Literal[
        "kids", "teens", "adults", "seniors",
        "family", "couples", "friends", "solo_travelers",
    ]]
    query_to_search: str | None # no Optional, no default


class PlaceRecommendationsSchema(BaseModel):
    recommended_places: list[RecommendedPlaceSchema]



class RecommendationUserPayload(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=20)
    from_city: str = Field(min_length=1, max_length=120)
    from_country: str = Field(min_length=1, max_length=120)
    bio: str = Field(default="", max_length=2000)
    languages: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    user_label: str | None




class GenerateRecommendationsRequest(BaseModel):
    trip_vacancy_id: int = Field(ge=1)
    destination_city: str = Field(default="", max_length=120)
    destination_country: str = Field(default="", max_length=120)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str = Field(default="", max_length=5000)
    planned_activities: str = Field(default="", max_length=5000)
    planned_destinations: str = Field(default="", max_length=5000)
    transportation_preference: str = Field(default="", max_length=120)
    accommodation_preference: str = Field(default="", max_length=120)
    min_budget: float = Field(default=0.0, ge=0)
    max_budget: float = Field(default=0.0, ge=0)
    users: list[RecommendationUserPayload] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates_and_budget(self) -> "GenerateRecommendationsRequest":
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be greater than or equal to start_date")
        if self.max_budget < self.min_budget:
            raise ValueError("max_budget must be greater than or equal to min_budget")
        return self