import random
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.security import (create_access_token, get_password_hash,
                               verify_password)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service
from app.core.redis_client import get_redis_client



class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.redis = get_redis_client()

    async def register(
        self, email: str, password: str, role: str = "user"
    ) -> Tuple[bool, Optional[User], Optional[str], Optional[str]]:
        if await self.user_repo.exists_by_email(email):
            return False, None, None, "Email already registered"

        if len(password) < 8:
            return False, None, None, "Password must be at least 8 characters long"

        hashed_password = get_password_hash(password)
        try:
            user = await self.user_repo.create(
                email=email, password=hashed_password, role=role
            )

            verification_code = await self._generate_verification_code(user.id, user.email)

            await self._send_verification_email(user.id, user.email, verification_code)
            return True, user, verification_code, None
        except Exception as e:
            return False, None, None, f"Registration failed: {str(e)}"

    async def login(
        self, email: str, password: str
    ) -> Tuple[bool, Optional[str], Optional[User], Optional[str]]:

        user = await self.user_repo.get_by_email(email)
        if not user:
            return False, None, None, "Invalid email or password"

        if not verify_password(password, user.password):
            return False, None, None, "Invalid email or password"
        if not user.is_active:
            return False, None, None, "Account is deactivated"

        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )

        return True, access_token, user, None

    async def request_password_reset(
        self, email: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return True, None, None

        reset_token = secrets.token_urlsafe(32)
        # Store reset token in Redis with 1 hour expiration
        await self.redis.set(
            f"reset_token:{reset_token}",
            {"user_id": user.id, "email": email},
            expire=3600
        )

        # Send password reset email
        try:
            await email_service.send_password_reset_email(email, reset_token)
        except Exception as e:
            print(f"Failed to send password reset email: {e}")

        return True, reset_token, None

    async def reset_password(
        self, token: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        # Get reset token data from Redis
        token_data = await self.redis.get(f"reset_token:{token}")
        if not token_data:
            return False, "Invalid or expired reset token"

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"

        hashed_password = get_password_hash(new_password)
        user = await self.user_repo.update_password(
            token_data["user_id"], hashed_password
        )

        if not user:
            return False, "Failed to update password"

        # Delete used token from Redis
        await self.redis.delete(f"reset_token:{token}")

        return True, None

    async def _generate_verification_code(self, user_id: int, email: str) -> str:
        """Generate a 4-digit verification code."""
        code = str(random.randint(1000, 9999))

        # Store verification code in Redis with 60 minutes expiration
        await self.redis.set(
            f"verification_code:{user_id}",
            {
                "code": code,
                "email": email,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(minutes=60)).isoformat(),
                "attempts": 0,
                "max_attempts": 5,
            },
            expire=3600  # 60 minutes
        )
        return code

    async def _send_verification_email(
        self, user_id: int, email: str, code: str
    ) -> bool:
        """Send verification email to user."""
        try:
            await email_service.send_verification_email(email, code, user_id)
            return True
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            return False

    async def resend_verification_code(
        self, user_id: int
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False, None, "User not found"

        if user.is_verified:
            return False, None, "Email already verified"

        # Check existing code in Redis
        existing_code = await self.redis.get(f"verification_code:{user_id}")
        if existing_code:
            created_at = datetime.fromisoformat(existing_code["created_at"])
            time_since_last = datetime.utcnow() - created_at
            if time_since_last < timedelta(minutes=1):
                return False, None, "Please wait before requesting a new code"

        # Generate new code
        verification_code = await self._generate_verification_code(user_id, user.email)
        # Send verification email
        await self._send_verification_email(user_id, user.email, verification_code)

        return True, verification_code, None

    async def verify_email(
        self, user_id: int, verification_code: str
    ) -> Tuple[bool, Optional[str]]:
        
        # Get verification data from Redis
        verification_data = await self.redis.get(f"verification_code:{user_id}")

        if not verification_data:
            return False, "No verification code found. Please request a new one"

        expires_at = datetime.fromisoformat(verification_data["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.redis.delete(f"verification_code:{user_id}")
            return False, "Verification code has expired. Please request a new one"

        if verification_data["attempts"] >= verification_data["max_attempts"]:
            await self.redis.delete(f"verification_code:{user_id}")
            return (
                False,
                "Maximum verification attempts exceeded. Please request a new code",
            )

        verification_data["attempts"] += 1

        if verification_data["code"] != verification_code:
            # Update attempts in Redis
            await self.redis.set(
                f"verification_code:{user_id}",
                verification_data,
                expire=3600
            )
            remaining_attempts = (
                verification_data["max_attempts"] - verification_data["attempts"]
            )
            return (
                False,
                f"Invalid verification code. {remaining_attempts} attempts remaining",
            )

        user = await self.user_repo.verify_user(user_id)

        if not user:
            return False, "User not found"

        # Delete verification code from Redis after successful verification
        await self.redis.delete(f"verification_code:{user_id}")

        # Send welcome email after successful verification
        try:
            await email_service.send_welcome_email(user.email)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")

        return True, None

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False, "User not found"

        if not verify_password(current_password, user.password):
            return False, "Current password is incorrect"

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"

        hashed_password = get_password_hash(new_password)
        updated_user = await self.user_repo.update_password(user_id, hashed_password)

        if not updated_user:
            return False, "Failed to update password"

        return True, None

    async def get_current_user(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
