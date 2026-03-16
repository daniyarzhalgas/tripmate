from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.trip_plan import TripPlanResponse
from app.services.trip_vacancy_service import TripVacancyService

router = APIRouter(prefix="/trip-plans", tags=["Trip Plans"])


@router.get("/{trip_vacancy_id}", response_model=TripPlanResponse)
async def get_trip_plan_by_trip_vacancy_id(
    trip_vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get generated trip plan by trip vacancy ID (members only)."""
    trip_vacancy_service = TripVacancyService(db)

    success, plan, error = await trip_vacancy_service.get_trip_plan(
        trip_vacancy_id=trip_vacancy_id,
        user_id=current_user.id,
    )

    if not success:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if error in {"Trip vacancy not found", "Trip plan not found"}
            else status.HTTP_403_FORBIDDEN
            if error == "You don't have permission to view this trip plan"
            else status.HTTP_409_CONFLICT
            if error == "we generating please wait"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=error)

    return TripPlanResponse.model_validate(plan)
