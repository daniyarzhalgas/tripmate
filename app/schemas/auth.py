from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    id: str
    email: EmailStr
    name: str
    isNewUser: bool
    profileComplete: bool


class LoginData(BaseModel):
    user: UserInfo
    accessToken: str
    refreshToken: str


class LoginResponse(BaseModel):
    success: bool = True
    data: LoginData


class ErrorInfo(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorInfo


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    dateOfBirth: date
    gender: str


class RegisterData(BaseModel):
    userId: str
    email: EmailStr
    verificationRequired: bool
    message: str


class RegisterResponse(BaseModel):
    success: bool = True
    data: RegisterData


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


class VerifyEmailData(BaseModel):
    verified: bool
    accessToken: str
    refreshToken: str


class VerifyEmailResponse(BaseModel):
    success: bool = True
    data: VerifyEmailData


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    success: bool = True
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class RefreshTokenData(BaseModel):
    accessToken: str
    refreshToken: str


class RefreshTokenResponse(BaseModel):
    success: bool = True
    data: RefreshTokenData


class LogoutRequest(BaseModel):
    refreshToken: str

