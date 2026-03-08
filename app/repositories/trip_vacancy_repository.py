from datetime import date
from typing import List, Optional

from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.trip_vacancy import TripVacancy
from app.models.user import User
from app.models.profile import Profile


class TripVacancyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= CREATE =============
    async def create(self, requester_id: int, **kwargs) -> TripVacancy:
        """Create a new trip vacancy."""
        trip_vacancy = TripVacancy(requester_id=requester_id, **kwargs)
        self.db.add(trip_vacancy)
        await self.db.commit()
        await self.db.refresh(trip_vacancy)
        return trip_vacancy

    # ============= READ =============
    async def get_by_id(self, trip_vacancy_id: int) -> Optional[TripVacancy]:
        """Get trip vacancy by ID."""
        query = select(TripVacancy).filter(TripVacancy.id == trip_vacancy_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_requester_id(
        self, requester_id: int, skip: int = 0, limit: int = 100
    ) -> List[TripVacancy]:
        """Get all trip vacancies for a specific requester."""
        query = (
            select(TripVacancy)
            .filter(TripVacancy.requester_id == requester_id)
            .offset(skip)
            .limit(limit)
            .order_by(TripVacancy.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        destination_city: Optional[str] = None,
        destination_country: Optional[str] = None,
        status: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        gender_preference: Optional[str] = None,
        from_city: Optional[str] = None,
        from_country: Optional[str] = None,
    ) -> List[TripVacancy]:
        """Get all trip vacancies with optional filters."""
        query = select(TripVacancy)
        
        # Join with User and Profile if we need to filter by requester's location
        if from_city or from_country:
            query = query.join(User, TripVacancy.requester_id == User.id)
            query = query.join(Profile, User.id == Profile.user_id)

        # Apply filters
        if destination_city:
            query = query.filter(TripVacancy.destination_city == destination_city)

        if destination_country:
            query = query.filter(TripVacancy.destination_country == destination_country)

        if status:
            query = query.filter(TripVacancy.status == status)

        if start_date_from:
            query = query.filter(TripVacancy.start_date >= start_date_from)

        if start_date_to:
            query = query.filter(TripVacancy.start_date <= start_date_to)

        if min_age is not None:
            query = query.filter(
                (TripVacancy.min_age == None) | (TripVacancy.min_age <= min_age)
            )

        if max_age is not None:
            query = query.filter(
                (TripVacancy.max_age == None) | (TripVacancy.max_age >= max_age)
            )

        if min_budget is not None:
            query = query.filter(
                (TripVacancy.max_budget == None) | (TripVacancy.max_budget >= min_budget)
            )

        if max_budget is not None:
            query = query.filter(
                (TripVacancy.min_budget == None) | (TripVacancy.min_budget <= max_budget)
            )

        if gender_preference:
            gender_lower = gender_preference.lower()

            query = query.filter(
                (sql_func.lower(TripVacancy.gender_preference) == "any") |
                (sql_func.lower(TripVacancy.gender_preference) == gender_lower)
            )
        if from_city:
            query = query.filter(Profile.city == from_city)

        if from_country:
            query = query.filter(Profile.country == from_country)

        query = query.offset(skip).limit(limit).order_by(TripVacancy.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        destination_city: Optional[str] = None,
        destination_country: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count trip vacancies with optional filters."""
        query = select(TripVacancy)

        if destination_city:
            query = query.filter(TripVacancy.destination_city == destination_city)

        if destination_country:
            query = query.filter(TripVacancy.destination_country == destination_country)

        if status:
            query = query.filter(TripVacancy.status == status)

        result = await self.db.execute(query)
        return len(result.scalars().all())

    # ============= UPDATE =============
    async def update(self, trip_vacancy_id: int, **kwargs) -> Optional[TripVacancy]:
        """Update trip vacancy fields."""
        trip_vacancy = await self.get_by_id(trip_vacancy_id)
        if not trip_vacancy:
            return None

        for key, value in kwargs.items():
            if hasattr(trip_vacancy, key) and value is not None:
                setattr(trip_vacancy, key, value)

        await self.db.commit()
        await self.db.refresh(trip_vacancy)
        return trip_vacancy

    async def update_status(
        self, trip_vacancy_id: int, status: str
    ) -> Optional[TripVacancy]:
        """Update trip vacancy status."""
        return await self.update(trip_vacancy_id, status=status)

    # ============= DELETE =============
    async def delete(self, trip_vacancy_id: int) -> bool:
        """Delete a trip vacancy."""
        trip_vacancy = await self.get_by_id(trip_vacancy_id)
        if not trip_vacancy:
            return False

        await self.db.delete(trip_vacancy)
        await self.db.commit()
        return True
