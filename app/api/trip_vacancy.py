from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.trip_vacancy import (
    MessageResponse,
    TripVacancyCreateRequest,
    TripVacancyResponse,
    TripVacancyUpdateRequest,
)
from app.services.trip_vacancy_service import TripVacancyService

router = APIRouter(prefix="/trip-vacancies", tags=["Trip Vacancies"])


# ============= TRIP VACANCY CRUD =============
@router.post(
    "", response_model=TripVacancyResponse, status_code=status.HTTP_201_CREATED
)
async def create_trip_vacancy(
    request: TripVacancyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trip vacancy."""
    trip_vacancy_service = TripVacancyService(db)

    success, trip_vacancy, error = await trip_vacancy_service.create_trip_vacancy(
        requester_id=current_user.id, **request.model_dump()
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return trip_vacancy


@router.get("/me", response_model=List[TripVacancyResponse])
async def get_my_trip_vacancies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all trip vacancies created by the current user."""
    trip_vacancy_service = TripVacancyService(db)

    trip_vacancies = await trip_vacancy_service.get_my_trip_vacancies(
        requester_id=current_user.id, skip=skip, limit=limit
    )

    return trip_vacancies


@router.get("/{trip_vacancy_id}", response_model=TripVacancyResponse)
async def get_trip_vacancy(
    trip_vacancy_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a trip vacancy by ID."""
    trip_vacancy_service = TripVacancyService(db)

    trip_vacancy = await trip_vacancy_service.get_trip_vacancy_by_id(trip_vacancy_id)

    if not trip_vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip vacancy not found",
        )

    return trip_vacancy


@router.get("", response_model=List[TripVacancyResponse])
async def get_all_trip_vacancies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    destination_city: Optional[str] = None,
    destination_country: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    min_age: Optional[int] = Query(None, ge=0, le=150),
    max_age: Optional[int] = Query(None, ge=0, le=150),
    min_budget: Optional[float] = Query(None, ge=0),
    max_budget: Optional[float] = Query(None, ge=0),
    gender_preference: Optional[str] = Query(None, regex="^(male|female|any)$"),
    from_city: Optional[str] = None,
    from_country: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all trip vacancies with optional filters."""
    trip_vacancy_service = TripVacancyService(db)

    trip_vacancies = await trip_vacancy_service.get_all_trip_vacancies(
        skip=skip,
        limit=limit,
        destination_city=destination_city,
        destination_country=destination_country,
        status=status_filter,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        min_age=min_age,
        max_age=max_age,
        min_budget=min_budget,
        max_budget=max_budget,
        gender_preference=gender_preference,
        from_city=from_city,
        from_country=from_country,
    )

    return trip_vacancies


@router.put("/{trip_vacancy_id}", response_model=TripVacancyResponse)
async def update_trip_vacancy(
    trip_vacancy_id: int,
    request: TripVacancyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a trip vacancy."""
    trip_vacancy_service = TripVacancyService(db)

    success, trip_vacancy, error = await trip_vacancy_service.update_trip_vacancy(
        trip_vacancy_id=trip_vacancy_id,
        requester_id=current_user.id,
        **request.model_dump(exclude_unset=True),
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return trip_vacancy


@router.patch("/{trip_vacancy_id}/status", response_model=TripVacancyResponse)
async def update_trip_vacancy_status(
    trip_vacancy_id: int,
    status_value: str = Query(..., alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update trip vacancy status."""
    trip_vacancy_service = TripVacancyService(db)

    success, trip_vacancy, error = await trip_vacancy_service.update_status(
        trip_vacancy_id=trip_vacancy_id,
        requester_id=current_user.id,
        status=status_value,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return trip_vacancy


@router.delete("/{trip_vacancy_id}", response_model=MessageResponse)
async def delete_trip_vacancy(
    trip_vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a trip vacancy."""
    trip_vacancy_service = TripVacancyService(db)

    success, error = await trip_vacancy_service.delete_trip_vacancy(
        trip_vacancy_id=trip_vacancy_id, requester_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {"message": "Trip vacancy deleted successfully"}
