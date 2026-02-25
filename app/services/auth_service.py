import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Tuple

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.repositories.auth_repository import auth_repository
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    ErrorInfo,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)


def _generate_numeric_code(length: int = 6) -> str:
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


def _generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def _error(code: str, message: str) -> ErrorResponse:
    return ErrorResponse(success=False, error=ErrorInfo(code=code, message=message))


class AuthService:
    async def register(
        self,
        db: AsyncSession,
        payload: RegisterRequest,
    ):
        existing = await user_repository.get_by_email(db, payload.email)
        if existing:
            return _error("EMAIL_TAKEN", "Email is already registered")

        password_hash = get_password_hash(payload.password)

        user = await user_repository.create(
            db,
            email=payload.email,
            password_hash=password_hash,
            first_name=payload.firstName,
            last_name=payload.lastName,
            date_of_birth=payload.dateOfBirth,
            gender=payload.gender,
        )
        user.profile_complete = True

        code = _generate_numeric_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        await auth_repository.create_verification_code(
            db,
            email=user.email,
            code=code,
            expires_at=expires_at,
        )

        await send_verification_email(email=user.email, code=code)

        response = RegisterResponse(
            data={
                "userId": str(user.id),
                "email": user.email,
                "verificationRequired": True,
                "message": "Verification code sent to your email",
            }
        )
        return response

    async def verify_email(
        self,
        db: AsyncSession,
        payload: VerifyEmailRequest,
    ):
        user = await user_repository.get_by_email(db, payload.email)
        if not user:
            return _error("USER_NOT_FOUND", "User not found")

        if user.is_verified:
            access_token, refresh_token = await self._issue_tokens_for_user(db, str(user.id))
            return {
                "success": True,
                "data": {
                    "verified": True,
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                },
            }

        record = await auth_repository.get_active_verification_code(
            db,
            email=payload.email,
            code=payload.code,
        )
        if not record:
            return _error("INVALID_CODE", "Invalid or expired verification code")

        await auth_repository.mark_verification_used(db, record)
        await user_repository.set_verified(db, user)

        await send_welcome_email(email=user.email, first_name=user.first_name)

        access_token, refresh_token = await self._issue_tokens_for_user(db, str(user.id))

        return {
            "success": True,
            "data": {
                "verified": True,
                "accessToken": access_token,
                "refreshToken": refresh_token,
            },
        }

    async def resend_verification(self, db: AsyncSession, email: str):
        user = await user_repository.get_by_email(db, email)
        if not user:
            return _error("USER_NOT_FOUND", "User not found")

        if user.is_verified:
            return _error("ALREADY_VERIFIED", "Email already verified")

        code = _generate_numeric_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        await auth_repository.create_verification_code(
            db,
            email=user.email,
            code=code,
            expires_at=expires_at,
        )

        await send_verification_email(email=user.email, code=code)

        return {
            "success": True,
            "message": "Verification code resent to your email",
        }

    async def login(self, db: AsyncSession, payload: LoginRequest):
        user = await user_repository.get_by_email(db, payload.email)
        if not user:
            return _error("INVALID_CREDENTIALS", "Invalid email or password")

        if not verify_password(payload.password, user.password):
            return _error("INVALID_CREDENTIALS", "Invalid email or password")

        if not user.is_verified:
            return _error("EMAIL_NOT_VERIFIED", "Email is not verified")

        is_new_user = not user.has_logged_in
        await user_repository.mark_logged_in(db, user)

        access_token, refresh_token = await self._issue_tokens_for_user(db, str(user.id))

        user_info = {
            "id": str(user.id),
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}",
            "isNewUser": is_new_user,
            "profileComplete": bool(user.profile_complete),
        }
        data = {
            "user": user_info,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }
        return LoginResponse(data=data)

    async def forgot_password(self, db: AsyncSession, email: str):
        user = await user_repository.get_by_email(db, email)
        if user:
            token = _generate_reset_token()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            await auth_repository.create_password_reset_token(
                db,
                email=email,
                token=token,
                expires_at=expires_at,
            )
            await send_password_reset_email(email=email, token=token)

        return {
            "success": True,
            "message": "If an account with that email exists, a reset link has been sent",
        }

    async def reset_password(self, db: AsyncSession, payload: ResetPasswordRequest):
        record = await auth_repository.get_active_password_reset_token(db, token=payload.token)
        if not record:
            return _error("INVALID_TOKEN", "Invalid or expired reset token")

        user = await user_repository.get_by_email(db, record.email)
        if not user:
            return _error("USER_NOT_FOUND", "User not found")

        await auth_repository.mark_password_reset_token_used(db, record)

        password_hash = get_password_hash(payload.newPassword)
        await user_repository.update_password(db, user, password_hash)
        await auth_repository.revoke_all_user_refresh_tokens(db, str(user.id))

        return {
            "success": True,
            "message": "Password has been reset successfully",
        }

    async def refresh_tokens(
        self,
        db: AsyncSession,
        payload: RefreshTokenRequest,
    ):
        try:
            decoded = decode_token(payload.refreshToken)
        except JWTError:
            return _error("INVALID_TOKEN", "Invalid refresh token")

        if decoded.get("type") != "refresh":
            return _error("INVALID_TOKEN", "Invalid refresh token type")

        record = await auth_repository.get_refresh_token(db, token=payload.refreshToken)
        if not record:
            return _error("INVALID_TOKEN", "Refresh token has expired or been revoked")

        user_id = decoded.get("sub")
        if not user_id or str(record.user_id) != str(user_id):
            return _error("INVALID_TOKEN", "Invalid refresh token subject")

        await auth_repository.revoke_refresh_token(db, record)

        access_token, new_refresh_token = await self._issue_tokens_for_user(db, user_id)

        return RefreshTokenResponse(
            data={
                "accessToken": access_token,
                "refreshToken": new_refresh_token,
            }
        )

    async def logout(self, db: AsyncSession, payload: LogoutRequest):
        try:
            decoded = decode_token(payload.refreshToken)
        except JWTError:
            return {
                "success": True,
                "message": "Logged out",
            }

        if decoded.get("type") != "refresh":
            return {
                "success": True,
                "message": "Logged out",
            }

        record = await auth_repository.get_refresh_token(db, token=payload.refreshToken)
        if record:
            await auth_repository.revoke_refresh_token(db, record)

        return {
            "success": True,
            "message": "Logged out",
        }

    async def _issue_tokens_for_user(self, db: AsyncSession, user_id: str) -> Tuple[str, str]:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        decoded = decode_token(refresh_token)
        exp_timestamp = decoded.get("exp")
        if exp_timestamp is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        else:
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        await auth_repository.create_refresh_token(
            db,
            user_id=user_id,
            token=refresh_token,
            expires_at=expires_at,
        )

        return access_token, refresh_token


auth_service = AuthService()

