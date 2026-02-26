from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = ProfileRepository(db)

    # ============= CREATE =============
    async def create_profile(
        self, user_id: int, **profile_data
    ) -> Tuple[bool, Optional[Profile], Optional[str]]:
        """Create a new profile for a user."""
        try:
            # Check if profile already exists for this user
            if await self.profile_repo.exists_by_user_id(user_id):
                return False, None, "Profile already exists for this user"

            profile = await self.profile_repo.create(user_id=user_id, **profile_data)
            return True, profile, None
        except Exception as e:
            return False, None, f"Failed to create profile: {str(e)}"

    # ============= READ =============
    async def get_profile_by_id(
        self, profile_id: int, include_relations: bool = False
    ) -> Optional[Profile]:
        """Get profile by ID."""
        if include_relations:
            return await self.profile_repo.get_with_relations(profile_id)
        return await self.profile_repo.get_by_id(profile_id)

    async def get_profile_by_user_id(
        self, user_id: int, include_relations: bool = False
    ) -> Optional[Profile]:
        """Get profile by user ID."""
        if include_relations:
            return await self.profile_repo.get_by_user_id_with_relations(user_id)
        return await self.profile_repo.get_by_user_id(user_id)

    async def get_all_profiles(
        self,
        skip: int = 0,
        limit: int = 100,
        country: Optional[str] = None,
        city: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> List[Profile]:
        """Get all profiles with optional filters."""
        return await self.profile_repo.get_all(
            skip=skip,
            limit=limit,
            country=country,
            city=city,
            gender=gender,
        )

    # ============= UPDATE =============
    async def update_profile(
        self, profile_id: int, **update_data
    ) -> Tuple[bool, Optional[Profile], Optional[str]]:
        """Update profile information."""
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}

            if not update_data:
                profile = await self.profile_repo.get_by_id(profile_id)
                return True, profile, None

            profile = await self.profile_repo.update(profile_id, **update_data)

            if not profile:
                return False, None, "Profile not found"

            return True, profile, None
        except Exception as e:
            return False, None, f"Failed to update profile: {str(e)}"

    async def update_profile_by_user_id(
        self, user_id: int, **update_data
    ) -> Tuple[bool, Optional[Profile], Optional[str]]:
        """Update profile by user ID."""
        profile = await self.profile_repo.get_by_user_id(user_id)

        if not profile:
            return False, None, "Profile not found"

        return await self.update_profile(profile.id, **update_data)

    # ============= DELETE =============
    async def delete_profile(self, profile_id: int) -> Tuple[bool, Optional[str]]:
        """Delete a profile."""
        try:
            success = await self.profile_repo.delete(profile_id)

            if not success:
                return False, "Profile not found"

            return True, None
        except Exception as e:
            return False, f"Failed to delete profile: {str(e)}"

    async def delete_profile_by_user_id(
        self, user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Delete profile by user ID."""
        profile = await self.profile_repo.get_by_user_id(user_id)

        if not profile:
            return False, "Profile not found"

        return await self.delete_profile(profile.id)

    # ============= LANGUAGES =============
    async def add_language(
        self, profile_id: int, language_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Add a language to profile."""
        try:
            result = await self.profile_repo.add_language(profile_id, language_id)

            if not result:
                return False, "Failed to add language"

            return True, None
        except Exception as e:
            return False, f"Failed to add language: {str(e)}"

    async def remove_language(
        self, profile_id: int, language_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Remove a language from profile."""
        try:
            success = await self.profile_repo.remove_language(profile_id, language_id)

            if not success:
                return False, "Language not found in profile"

            return True, None
        except Exception as e:
            return False, f"Failed to remove language: {str(e)}"

    async def set_languages(
        self, profile_id: int, language_ids: List[int]
    ) -> Tuple[bool, Optional[str]]:
        """Replace all languages for a profile."""
        try:
            await self.profile_repo.set_languages(profile_id, language_ids)
            return True, None
        except Exception as e:
            return False, f"Failed to set languages: {str(e)}"

    async def get_profile_languages(self, profile_id: int):
        """Get all languages for a profile."""
        return await self.profile_repo.get_profile_languages(profile_id)

    # ============= INTERESTS =============
    async def add_interest(
        self, profile_id: int, interest_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Add an interest to profile."""
        try:
            result = await self.profile_repo.add_interest(profile_id, interest_id)

            if not result:
                return False, "Failed to add interest"

            return True, None
        except Exception as e:
            return False, f"Failed to add interest: {str(e)}"

    async def remove_interest(
        self, profile_id: int, interest_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Remove an interest from profile."""
        try:
            success = await self.profile_repo.remove_interest(profile_id, interest_id)

            if not success:
                return False, "Interest not found in profile"

            return True, None
        except Exception as e:
            return False, f"Failed to remove interest: {str(e)}"

    async def set_interests(
        self, profile_id: int, interest_ids: List[int]
    ) -> Tuple[bool, Optional[str]]:
        """Replace all interests for a profile."""
        try:
            await self.profile_repo.set_interests(profile_id, interest_ids)
            return True, None
        except Exception as e:
            return False, f"Failed to set interests: {str(e)}"

    async def get_profile_interests(self, profile_id: int):
        """Get all interests for a profile."""
        return await self.profile_repo.get_profile_interests(profile_id)

    # ============= TRAVEL STYLES =============
    async def add_travel_style(
        self, profile_id: int, travel_style_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Add a travel style to profile."""
        try:
            result = await self.profile_repo.add_travel_style(
                profile_id, travel_style_id
            )

            if not result:
                return False, "Failed to add travel style"

            return True, None
        except Exception as e:
            return False, f"Failed to add travel style: {str(e)}"

    async def remove_travel_style(
        self, profile_id: int, travel_style_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Remove a travel style from profile."""
        try:
            success = await self.profile_repo.remove_travel_style(
                profile_id, travel_style_id
            )

            if not success:
                return False, "Travel style not found in profile"

            return True, None
        except Exception as e:
            return False, f"Failed to remove travel style: {str(e)}"

    async def set_travel_styles(
        self, profile_id: int, travel_style_ids: List[int]
    ) -> Tuple[bool, Optional[str]]:
        """Replace all travel styles for a profile."""
        try:
            await self.profile_repo.set_travel_styles(profile_id, travel_style_ids)
            return True, None
        except Exception as e:
            return False, f"Failed to set travel styles: {str(e)}"

    async def get_profile_travel_styles(self, profile_id: int):
        """Get all travel styles for a profile."""
        return await self.profile_repo.get_profile_travel_styles(profile_id)

    # ============= HELPERS =============
    async def get_all_languages(self):
        """Get all available languages."""
        return await self.profile_repo.get_all_languages()

    async def get_all_interests(self):
        """Get all available interests."""
        return await self.profile_repo.get_all_interests()

    async def get_all_travel_styles(self):
        """Get all available travel styles."""
        return await self.profile_repo.get_all_travel_styles()
