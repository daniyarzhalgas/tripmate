from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============= Request Schemas =============
class ProfileCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(..., min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    nationality: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    telegram_handle: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    nationality: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    telegram_handle: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None


class LanguageBase(BaseModel):
    language_id: int


class InterestBase(BaseModel):
    interest_id: int


class TravelStyleBase(BaseModel):
    travel_style_id: int


# ============= Response Schemas =============
class LanguageResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class InterestResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TravelStyleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserLanguageResponse(BaseModel):
    id: int
    language_id: int
    language: LanguageResponse

    class Config:
        from_attributes = True


class UserInterestResponse(BaseModel):
    id: int
    interest_id: int
    interest: InterestResponse

    class Config:
        from_attributes = True


class UserTravelStyleResponse(BaseModel):
    id: int
    travel_style_id: int
    travel_style: TravelStyleResponse

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    country: Optional[str] = None
    city: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    telegram_handle: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileDetailResponse(ProfileResponse):
    languages: List[UserLanguageResponse] = []
    interests: List[UserInterestResponse] = []
    travel_styles: List[UserTravelStyleResponse] = []

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
