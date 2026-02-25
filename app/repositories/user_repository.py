from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        date_of_birth,
        gender: str,
    ) -> User:
        user = User(
            email=email,
            password=password_hash,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def set_verified(self, db: AsyncSession, user: User) -> User:
        user.is_verified = True
        await db.flush()
        await db.refresh(user)
        return user

    async def update_password(self, db: AsyncSession, user: User, password_hash: str) -> User:
        user.password = password_hash
        await db.flush()
        await db.refresh(user)
        return user

    async def mark_logged_in(self, db: AsyncSession, user: User) -> User:
        user.has_logged_in = True
        await db.flush()
        await db.refresh(user)
        return user


user_repository = UserRepository()

