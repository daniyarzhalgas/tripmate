from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    ErrorResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResendVerificationRequest,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.services.auth_service import auth_service


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse | ErrorResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.login(db, payload)


@router.post("/register", response_model=RegisterResponse | ErrorResponse)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.register(db, payload)


@router.post("/verify-email", response_model=VerifyEmailResponse | ErrorResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.verify_email(db, payload)
    if isinstance(result, dict) and result.get("success") and "data" in result:
        return VerifyEmailResponse(**result)
    if isinstance(result, dict) and not result.get("success"):
        return ErrorResponse(**result)
    return result


@router.post("/resend-verification", response_model=MessageResponse | ErrorResponse)
async def resend_verification(
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.resend_verification(db, payload.email)
    if result.get("success"):
        return MessageResponse(**result)
    return ErrorResponse(**result)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.forgot_password(db, payload.email)
    return MessageResponse(**result)


@router.post("/reset-password", response_model=MessageResponse | ErrorResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.reset_password(db, payload)
    if result.get("success"):
        return MessageResponse(**result)
    return ErrorResponse(**result)


@router.post("/refresh-token", response_model=RefreshTokenResponse | ErrorResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.refresh_tokens(db, payload)
    if isinstance(result, RefreshTokenResponse):
        return result
    if isinstance(result, dict) and result.get("success"):
        return RefreshTokenResponse(**result)
    return ErrorResponse(**result)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await auth_service.logout(db, payload)
    return MessageResponse(**result)

