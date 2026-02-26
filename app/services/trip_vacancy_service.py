from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_vacancy import TripVacancy
from app.repositories.trip_vacancy_repository import TripVacancyRepository


class TripVacancyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.trip_vacancy_repo = TripVacancyRepository(db)

    # ============= CREATE =============
    async def create_trip_vacancy(
        self, requester_id: int, **trip_vacancy_data
    ) -> Tuple[bool, Optional[TripVacancy], Optional[str]]:
        """Create a new trip vacancy."""
        try:
            # Validate dates
            start_date = trip_vacancy_data.get("start_date")
            end_date = trip_vacancy_data.get("end_date")

            if start_date and end_date and start_date >= end_date:
                return False, None, "End date must be after start date"

            # Validate budget
            min_budget = trip_vacancy_data.get("min_budget")
            max_budget = trip_vacancy_data.get("max_budget")

            if (
                min_budget is not None
                and max_budget is not None
                and min_budget > max_budget
            ):
                return (
                    False,
                    None,
                    "Max budget must be greater than or equal to min budget",
                )

            # Validate age
            min_age = trip_vacancy_data.get("min_age")
            max_age = trip_vacancy_data.get("max_age")

            if min_age is not None and max_age is not None and min_age > max_age:
                return False, None, "Max age must be greater than or equal to min age"

            trip_vacancy = await self.trip_vacancy_repo.create(
                requester_id=requester_id, **trip_vacancy_data
            )
            return True, trip_vacancy, None
        except Exception as e:
            return False, None, f"Failed to create trip vacancy: {str(e)}"

    # ============= READ =============
    async def get_trip_vacancy_by_id(
        self, trip_vacancy_id: int
    ) -> Optional[TripVacancy]:
        """Get trip vacancy by ID."""
        return await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)

    async def get_my_trip_vacancies(
        self, requester_id: int, skip: int = 0, limit: int = 100
    ) -> List[TripVacancy]:
        """Get all trip vacancies for the current user."""
        return await self.trip_vacancy_repo.get_by_requester_id(
            requester_id, skip=skip, limit=limit
        )

    async def get_all_trip_vacancies(
        self,
        skip: int = 0,
        limit: int = 100,
        destination_city: Optional[str] = None,
        destination_country: Optional[str] = None,
        status: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
    ) -> List[TripVacancy]:
        """Get all trip vacancies with optional filters."""
        return await self.trip_vacancy_repo.get_all(
            skip=skip,
            limit=limit,
            destination_city=destination_city,
            destination_country=destination_country,
            status=status,
            start_date_from=start_date_from,
            start_date_to=start_date_to,
        )

    # ============= UPDATE =============
    async def update_trip_vacancy(
        self, trip_vacancy_id: int, requester_id: int, **update_data
    ) -> Tuple[bool, Optional[TripVacancy], Optional[str]]:
        """Update trip vacancy information."""
        try:
            # Check if trip vacancy exists and belongs to the requester
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)

            if not trip_vacancy:
                return False, None, "Trip vacancy not found"

            if trip_vacancy.requester_id != requester_id:
                return (
                    False,
                    None,
                    "You don't have permission to update this trip vacancy",
                )

            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}

            if not update_data:
                return True, trip_vacancy, None

            # Validate dates if being updated
            start_date = update_data.get("start_date", trip_vacancy.start_date)
            end_date = update_data.get("end_date", trip_vacancy.end_date)

            if start_date and end_date and start_date >= end_date:
                return False, None, "End date must be after start date"

            # Validate budget if being updated
            min_budget = update_data.get("min_budget", trip_vacancy.min_budget)
            max_budget = update_data.get("max_budget", trip_vacancy.max_budget)

            if (
                min_budget is not None
                and max_budget is not None
                and min_budget > max_budget
            ):
                return (
                    False,
                    None,
                    "Max budget must be greater than or equal to min budget",
                )

            # Validate age if being updated
            min_age = update_data.get("min_age", trip_vacancy.min_age)
            max_age = update_data.get("max_age", trip_vacancy.max_age)

            if min_age is not None and max_age is not None and min_age > max_age:
                return False, None, "Max age must be greater than or equal to min age"

            updated_trip_vacancy = await self.trip_vacancy_repo.update(
                trip_vacancy_id, **update_data
            )

            return True, updated_trip_vacancy, None
        except Exception as e:
            return False, None, f"Failed to update trip vacancy: {str(e)}"

    async def update_status(
        self, trip_vacancy_id: int, requester_id: int, status: str
    ) -> Tuple[bool, Optional[TripVacancy], Optional[str]]:
        """Update trip vacancy status."""
        trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)

        if not trip_vacancy:
            return False, None, "Trip vacancy not found"

        if trip_vacancy.requester_id != requester_id:
            return (
                False,
                None,
                "You don't have permission to update this trip vacancy",
            )

        valid_statuses = ["open", "matched", "closed", "cancelled"]
        if status not in valid_statuses:
            return (
                False,
                None,
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        updated_trip_vacancy = await self.trip_vacancy_repo.update_status(
            trip_vacancy_id, status
        )
        return True, updated_trip_vacancy, None

    # ============= DELETE =============
    async def delete_trip_vacancy(
        self, trip_vacancy_id: int, requester_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Delete a trip vacancy."""
        try:
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)

            if not trip_vacancy:
                return False, "Trip vacancy not found"

            if trip_vacancy.requester_id != requester_id:
                return (
                    False,
                    "You don't have permission to delete this trip vacancy",
                )

            success = await self.trip_vacancy_repo.delete(trip_vacancy_id)

            if not success:
                return False, "Failed to delete trip vacancy"

            return True, None
        except Exception as e:
            return False, f"Failed to delete trip vacancy: {str(e)}"
