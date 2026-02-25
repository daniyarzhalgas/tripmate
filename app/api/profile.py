from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import ErrorResponse, ErrorInfo
from app.schemas.profile import ProfileMeData, ProfilePublicData, ProfileResponse


router = APIRouter(prefix="/api/profile", tags=["profile"])


def _calculate_age(date_of_birth: date) -> int:
    today = date.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


@router.get("/me", response_model=ProfileResponse)
async def get_own_profile(
    current_user: User = Depends(get_current_user),
):
    age = _calculate_age(current_user.date_of_birth)

    data = ProfileMeData(
        id=str(current_user.id),
        email=current_user.email,
        firstName=current_user.first_name,
        lastName=current_user.last_name,
        fullName=f"{current_user.first_name} {current_user.last_name}",
        dateOfBirth=current_user.date_of_birth,
        age=age,
        gender=current_user.gender,
        emailVerified=bool(current_user.is_verified),
        memberSince=current_user.created_at,
    )
    return ProfileResponse(data=data)


@router.get("/{user_id}", response_model=ProfileResponse | ErrorResponse)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await user_repository.get_by_id(db, user_id)
    if not user:
        return ErrorResponse(
            success=False,
            error=ErrorInfo(code="NOT_FOUND", message="User not found"),
        )

    age = _calculate_age(user.date_of_birth)

    data = ProfilePublicData(
        id=str(user.id),
        firstName=user.first_name,
        age=age,
        gender=user.gender,
        memberSince=user.created_at,
    )
    return ProfileResponse(data=data)

