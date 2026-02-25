from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordResetVerify(BaseModel):
    email: EmailStr
    reset_code: str = Field(..., min_length=4, max_length=4)
    new_password: str = Field(..., min_length=8)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class EmailVerificationRequest(BaseModel):
    user_id: int
    verification_code: str = Field(..., min_length=4, max_length=4)


class ResendVerificationRequest(BaseModel):
    user_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str
    verification_code: Optional[str] = None 


class MessageResponse(BaseModel):
    message: str