from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import EmailVerificationCode, PasswordResetToken, RefreshToken


class AuthRepository:
    async def create_verification_code(
        self,
        db: AsyncSession,
        *,
        email: str,
        code: str,
        expires_at: datetime,
    ) -> EmailVerificationCode:
        record = EmailVerificationCode(
            email=email,
            code=code,
            expires_at=expires_at,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def get_active_verification_code(
        self,
        db: AsyncSession,
        *,
        email: str,
        code: str,
    ) -> Optional[EmailVerificationCode]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(EmailVerificationCode)
            .where(
                and_(
                    EmailVerificationCode.email == email,
                    EmailVerificationCode.code == code,
                    EmailVerificationCode.used.is_(False),
                    EmailVerificationCode.expires_at > now,
                )
            )
            .order_by(EmailVerificationCode.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def mark_verification_used(
        self,
        db: AsyncSession,
        record: EmailVerificationCode,
    ) -> EmailVerificationCode:
        record.used = True
        await db.flush()
        await db.refresh(record)
        return record

    async def create_password_reset_token(
        self,
        db: AsyncSession,
        *,
        email: str,
        token: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        record = PasswordResetToken(
            email=email,
            token=token,
            expires_at=expires_at,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def get_active_password_reset_token(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> Optional[PasswordResetToken]:
        now = datetime.now(timezone.utc)
        stmt = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.used.is_(False),
                PasswordResetToken.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def mark_password_reset_token_used(
        self,
        db: AsyncSession,
        record: PasswordResetToken,
    ) -> PasswordResetToken:
        record.used = True
        await db.flush()
        await db.refresh(record)
        return record

    async def create_refresh_token(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken:
        record = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    async def get_refresh_token(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> Optional[RefreshToken]:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.token == token,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def revoke_refresh_token(
        self,
        db: AsyncSession,
        record: RefreshToken,
    ) -> RefreshToken:
        record.revoked = True
        await db.flush()
        await db.refresh(record)
        return record

    async def revoke_all_user_refresh_tokens(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        for record in result.scalars().all():
            record.revoked = True
        await db.flush()


auth_repository = AuthRepository()

