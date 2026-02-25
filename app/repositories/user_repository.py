from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.profile import Profile
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, email: str, password: str, role: str = "user") -> User:
        """Create a new user."""
        user = User(email=email, password=password, role=role)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(
        self, user_id: int, include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by ID."""
        query = select(User).filter(User.id == user_id)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(
        self, email: str, include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by email."""
        query = select(User).filter(User.email == email)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_profile(self, user_id: int) -> Optional[User]:
        """Get user with profile eagerly loaded."""
        query = (
            select(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .options(joinedload(User.profile))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_trip_vacancies(self, user_id: int) -> Optional[User]:
        """Get user with trip vacancies eagerly loaded."""
        query = (
            select(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .options(joinedload(User.trip_vacancies))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None,
    ) -> List[User]:
        """Get all users with optional filters."""
        query = select(User)

        # Apply filters
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)

        if role:
            query = query.filter(User.role == role)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        query = select(User.id).filter(User.email == email, User.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count(
        self,
        include_deleted: bool = False,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> int:
        """Count users with optional filters."""
        query = select(func.count()).select_from(User)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_email(self, user_id: int, new_email: str) -> Optional[User]:
        """Update user email."""
        return await self.update(user_id, email=new_email)

    async def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Update user password."""
        return await self.update(user_id, password=new_password)

    async def verify_user(self, user_id: int) -> Optional[User]:
        """Mark user as verified."""
        return await self.update(user_id, is_verified=True)

    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user account."""
        return await self.update(user_id, is_active=True)

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user account."""
        return await self.update(user_id, is_active=False)

    async def change_role(self, user_id: int, new_role: str) -> Optional[User]:
        """Change user role."""
        return await self.update(user_id, role=new_role)

    # ============= DELETE =============
    async def soft_delete(self, user_id: int) -> bool:
        """Soft delete a user (set deleted_at timestamp)."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.deleted_at = datetime.utcnow()
        user.is_active = False
        await self.db.commit()
        return True

    async def restore(self, user_id: int) -> Optional[User]:
        """Restore a soft-deleted user."""
        user = await self.get_by_id(user_id, include_deleted=True)
        if not user or user.deleted_at is None:
            return None

        user.deleted_at = None
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def hard_delete(self, user_id: int) -> bool:
        """Permanently delete a user from database."""
        user = await self.get_by_id(user_id, include_deleted=True)
        if not user:
            return False

        self.db.delete(user)
        await self.db.commit()
        return True
