from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class ProfileMeData(BaseModel):
    id: str
    email: EmailStr
    firstName: str
    lastName: str
    fullName: str
    dateOfBirth: date
    age: int
    gender: str
    emailVerified: bool
    memberSince: datetime


class ProfilePublicData(BaseModel):
    id: str
    firstName: str
    age: int
    gender: str
    memberSince: datetime


class ProfileResponse(BaseModel):
    success: bool = True
    data: ProfileMeData | ProfilePublicData

