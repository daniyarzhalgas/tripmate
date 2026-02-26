from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile import (
    InterestBase,
    InterestResponse,
    LanguageBase,
    LanguageResponse,
    MessageResponse,
    ProfileCreateRequest,
    ProfileDetailResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    TravelStyleBase,
    TravelStyleResponse,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# ============= PROFILE CRUD =============
@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    request: ProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a profile for the current user."""
    profile_service = ProfileService(db)

    success, profile, error = await profile_service.create_profile(
        user_id=current_user.id, **request.model_dump()
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return profile


@router.get("/me", response_model=ProfileDetailResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's profile with languages and interests."""
    profile_service = ProfileService(db)

    profile = await profile_service.get_profile_by_user_id(
        current_user.id, include_relations=True
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@router.get("/{profile_id}", response_model=ProfileDetailResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a profile by ID with languages and interests."""
    profile_service = ProfileService(db)

    profile = await profile_service.get_profile_by_id(
        profile_id, include_relations=True
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    profile_service = ProfileService(db)

    success, profile, error = await profile_service.update_profile_by_user_id(
        user_id=current_user.id, **request.model_dump(exclude_unset=True)
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return profile


@router.delete("/me", response_model=MessageResponse)
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the current user's profile."""
    profile_service = ProfileService(db)

    success, error = await profile_service.delete_profile_by_user_id(
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Profile deleted successfully"}


# ============= LANGUAGES =============
@router.post("/me/languages", response_model=MessageResponse)
async def add_language_to_profile(
    request: LanguageBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a language to the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.add_language(profile.id, request.language_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Language added successfully"}


@router.delete("/me/languages/{language_id}", response_model=MessageResponse)
async def remove_language_from_profile(
    language_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a language from the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.remove_language(profile.id, language_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Language removed successfully"}


@router.put("/me/languages", response_model=MessageResponse)
async def set_profile_languages(
    language_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace all languages for the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.set_languages(profile.id, language_ids)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Languages updated successfully"}


# ============= INTERESTS =============
@router.post("/me/interests", response_model=MessageResponse)
async def add_interest_to_profile(
    request: InterestBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add an interest to the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.add_interest(profile.id, request.interest_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Interest added successfully"}


@router.delete("/me/interests/{interest_id}", response_model=MessageResponse)
async def remove_interest_from_profile(
    interest_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove an interest from the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.remove_interest(profile.id, interest_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Interest removed successfully"}


@router.put("/me/interests", response_model=MessageResponse)
async def set_profile_interests(
    interest_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace all interests for the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.set_interests(profile.id, interest_ids)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Interests updated successfully"}


# ============= TRAVEL STYLES =============
@router.post("/me/travel-styles", response_model=MessageResponse)
async def add_travel_style_to_profile(
    request: TravelStyleBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a travel style to the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.add_travel_style(
        profile.id, request.travel_style_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Travel style added successfully"}


@router.delete("/me/travel-styles/{travel_style_id}", response_model=MessageResponse)
async def remove_travel_style_from_profile(
    travel_style_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a travel style from the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.remove_travel_style(
        profile.id, travel_style_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Travel style removed successfully"}


@router.put("/me/travel-styles", response_model=MessageResponse)
async def set_profile_travel_styles(
    travel_style_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Replace all travel styles for the current user's profile."""
    profile_service = ProfileService(db)

    # Get profile ID
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    success, error = await profile_service.set_travel_styles(
        profile.id, travel_style_ids
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Travel styles updated successfully"}


# ============= AVAILABLE OPTIONS =============
@router.get("/options/languages", response_model=List[LanguageResponse])
async def get_all_languages(
    db: AsyncSession = Depends(get_db),
):
    """Get all available languages."""
    profile_service = ProfileService(db)
    languages = await profile_service.get_all_languages()
    return languages


@router.get("/options/interests", response_model=List[InterestResponse])
async def get_all_interests(
    db: AsyncSession = Depends(get_db),
):
    """Get all available interests."""
    profile_service = ProfileService(db)
    interests = await profile_service.get_all_interests()
    return interests


@router.get("/options/travel-styles", response_model=List[TravelStyleResponse])
async def get_all_travel_styles(
    db: AsyncSession = Depends(get_db),
):
    """Get all available travel styles."""
    profile_service = ProfileService(db)
    travel_styles = await profile_service.get_all_travel_styles()
    return travel_styles
