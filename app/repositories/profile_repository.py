from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.profile import Profile
from app.models.interest import UserInterest, Interest
from app.models.language import UserLanguage, Language
from app.models.travel_style import UserTravelStyle, TravelStyle


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= CREATE =============
    async def create(self, user_id: int, **kwargs) -> Profile:
        """Create a new profile."""
        profile = Profile(user_id=user_id, **kwargs)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    # ============= READ =============
    async def get_by_id(self, profile_id: int) -> Optional[Profile]:
        """Get profile by ID."""
        query = select(Profile).filter(Profile.id == profile_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        """Get profile by user ID."""
        query = select(Profile).filter(Profile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_relations(self, profile_id: int) -> Optional[Profile]:
        """Get profile with languages, interests and travel styles eagerly loaded."""
        query = (
            select(Profile)
            .filter(Profile.id == profile_id)
            .options(
                joinedload(Profile.languages).joinedload(UserLanguage.language),
                joinedload(Profile.interests).joinedload(UserInterest.interest),
                joinedload(Profile.travel_styles).joinedload(
                    UserTravelStyle.travel_style
                ),
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_user_id_with_relations(self, user_id: int) -> Optional[Profile]:
        """Get profile by user ID with languages, interests and travel styles."""
        query = (
            select(Profile)
            .filter(Profile.user_id == user_id)
            .options(
                joinedload(Profile.languages).joinedload(UserLanguage.language),
                joinedload(Profile.interests).joinedload(UserInterest.interest),
                joinedload(Profile.travel_styles).joinedload(
                    UserTravelStyle.travel_style
                ),
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        country: Optional[str] = None,
        city: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> List[Profile]:
        """Get all profiles with optional filters."""
        query = select(Profile)

        # Apply filters
        if country:
            query = query.filter(Profile.country == country)

        if city:
            query = query.filter(Profile.city == city)

        if gender:
            query = query.filter(Profile.gender == gender)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def exists_by_user_id(self, user_id: int) -> bool:
        """Check if profile exists for user."""
        query = select(Profile.id).filter(Profile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    # ============= UPDATE =============
    async def update(self, profile_id: int, **kwargs) -> Optional[Profile]:
        """Update profile fields."""
        profile = await self.get_by_id(profile_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    # ============= DELETE =============
    async def delete(self, profile_id: int) -> bool:
        """Delete a profile."""
        profile = await self.get_by_id(profile_id)
        if not profile:
            return False

        await self.db.delete(profile)
        await self.db.commit()
        return True

    # ============= LANGUAGES =============
    async def add_language(
        self, profile_id: int, language_id: int
    ) -> Optional[UserLanguage]:
        """Add a language to profile."""
        # Check if already exists
        query = select(UserLanguage).filter(
            UserLanguage.profile_id == profile_id,
            UserLanguage.language_id == language_id,
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        user_language = UserLanguage(profile_id=profile_id, language_id=language_id)
        self.db.add(user_language)
        await self.db.commit()
        await self.db.refresh(user_language)
        return user_language

    async def remove_language(self, profile_id: int, language_id: int) -> bool:
        """Remove a language from profile."""
        query = select(UserLanguage).filter(
            UserLanguage.profile_id == profile_id,
            UserLanguage.language_id == language_id,
        )
        result = await self.db.execute(query)
        user_language = result.scalar_one_or_none()

        if not user_language:
            return False

        await self.db.delete(user_language)
        await self.db.commit()
        return True

    async def get_profile_languages(self, profile_id: int) -> List[UserLanguage]:
        """Get all languages for a profile."""
        query = (
            select(UserLanguage)
            .filter(UserLanguage.profile_id == profile_id)
            .options(joinedload(UserLanguage.language))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def set_languages(self, profile_id: int, language_ids: List[int]) -> bool:
        """Replace all languages for a profile."""
        # Remove existing languages
        query = select(UserLanguage).filter(UserLanguage.profile_id == profile_id)
        result = await self.db.execute(query)
        existing = result.scalars().all()

        for user_language in existing:
            await self.db.delete(user_language)

        # Add new languages
        for language_id in language_ids:
            user_language = UserLanguage(profile_id=profile_id, language_id=language_id)
            self.db.add(user_language)

        await self.db.commit()
        return True

    # ============= INTERESTS =============
    async def add_interest(
        self, profile_id: int, interest_id: int
    ) -> Optional[UserInterest]:
        """Add an interest to profile."""
        # Check if already exists
        query = select(UserInterest).filter(
            UserInterest.profile_id == profile_id,
            UserInterest.interest_id == interest_id,
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        user_interest = UserInterest(profile_id=profile_id, interest_id=interest_id)
        self.db.add(user_interest)
        await self.db.commit()
        await self.db.refresh(user_interest)
        return user_interest

    async def remove_interest(self, profile_id: int, interest_id: int) -> bool:
        """Remove an interest from profile."""
        query = select(UserInterest).filter(
            UserInterest.profile_id == profile_id,
            UserInterest.interest_id == interest_id,
        )
        result = await self.db.execute(query)
        user_interest = result.scalar_one_or_none()

        if not user_interest:
            return False

        await self.db.delete(user_interest)
        await self.db.commit()
        return True

    async def get_profile_interests(self, profile_id: int) -> List[UserInterest]:
        """Get all interests for a profile."""
        query = (
            select(UserInterest)
            .filter(UserInterest.profile_id == profile_id)
            .options(joinedload(UserInterest.interest))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def set_interests(self, profile_id: int, interest_ids: List[int]) -> bool:
        """Replace all interests for a profile."""
        # Remove existing interests
        query = select(UserInterest).filter(UserInterest.profile_id == profile_id)
        result = await self.db.execute(query)
        existing = result.scalars().all()

        for user_interest in existing:
            await self.db.delete(user_interest)

        # Add new interests
        for interest_id in interest_ids:
            user_interest = UserInterest(profile_id=profile_id, interest_id=interest_id)
            self.db.add(user_interest)

        await self.db.commit()
        return True

    # ============= TRAVEL STYLES =============
    async def add_travel_style(
        self, profile_id: int, travel_style_id: int
    ) -> Optional[UserTravelStyle]:
        """Add a travel style to profile."""
        # Check if already exists
        query = select(UserTravelStyle).filter(
            UserTravelStyle.profile_id == profile_id,
            UserTravelStyle.travel_style_id == travel_style_id,
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        user_travel_style = UserTravelStyle(
            profile_id=profile_id, travel_style_id=travel_style_id
        )
        self.db.add(user_travel_style)
        await self.db.commit()
        await self.db.refresh(user_travel_style)
        return user_travel_style

    async def remove_travel_style(self, profile_id: int, travel_style_id: int) -> bool:
        """Remove a travel style from profile."""
        query = select(UserTravelStyle).filter(
            UserTravelStyle.profile_id == profile_id,
            UserTravelStyle.travel_style_id == travel_style_id,
        )
        result = await self.db.execute(query)
        user_travel_style = result.scalar_one_or_none()

        if not user_travel_style:
            return False

        await self.db.delete(user_travel_style)
        await self.db.commit()
        return True

    async def get_profile_travel_styles(self, profile_id: int) -> List[UserTravelStyle]:
        """Get all travel styles for a profile."""
        query = (
            select(UserTravelStyle)
            .filter(UserTravelStyle.profile_id == profile_id)
            .options(joinedload(UserTravelStyle.travel_style))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def set_travel_styles(
        self, profile_id: int, travel_style_ids: List[int]
    ) -> bool:
        """Replace all travel styles for a profile."""
        # Remove existing travel styles
        query = select(UserTravelStyle).filter(UserTravelStyle.profile_id == profile_id)
        result = await self.db.execute(query)
        existing = result.scalars().all()

        for user_travel_style in existing:
            await self.db.delete(user_travel_style)

        # Add new travel styles
        for travel_style_id in travel_style_ids:
            user_travel_style = UserTravelStyle(
                profile_id=profile_id, travel_style_id=travel_style_id
            )
            self.db.add(user_travel_style)

        await self.db.commit()
        return True

    # ============= LANGUAGE/INTEREST/TRAVEL STYLE HELPERS =============
    async def get_all_languages(self) -> List[Language]:
        """Get all available languages."""
        query = select(Language)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_interests(self) -> List[Interest]:
        """Get all available interests."""
        query = select(Interest)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_travel_styles(self) -> List[TravelStyle]:
        """Get all available travel styles."""
        query = select(TravelStyle)
        result = await self.db.execute(query)
        return list(result.scalars().all())
