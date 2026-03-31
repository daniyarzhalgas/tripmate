from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.generated_trip_plan import GeneratedTripPlan
from app.models.recommended_place import RecommendedPlace
from app.schemas.recommendation import (PlaceRecommendationsSchema,
                                        RecommendedPlaceSchema)


class GeneratedTripPlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_trip_vacancy_id(
        self, trip_vacancy_id: int
    ) -> Optional[GeneratedTripPlan]:
        query = select(GeneratedTripPlan).filter(
            GeneratedTripPlan.trip_vacancy_id == trip_vacancy_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_trip_vacancy_id_with_places(
        self, trip_vacancy_id: int
    ) -> Optional[GeneratedTripPlan]:
        query = (
            select(GeneratedTripPlan)
            .options(selectinload(GeneratedTripPlan.recommended_places))
            .filter(GeneratedTripPlan.trip_vacancy_id == trip_vacancy_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def upsert_plan_response(
        self, trip_vacancy_id: int, planner_response: PlaceRecommendationsSchema
    ) -> GeneratedTripPlan:
        plan = await self.get_by_trip_vacancy_id(trip_vacancy_id)
        now = datetime.utcnow()
        raw = planner_response.model_dump()

        if not plan:
            plan = GeneratedTripPlan(
                trip_vacancy_id=trip_vacancy_id,
                raw_response=raw,
                generation_requested_at=now,
                generated_at=now,
            )
            self.db.add(plan)
            await self.db.flush()
        else:
            plan.raw_response = raw
            if not plan.generation_requested_at:
                plan.generation_requested_at = now
            plan.generated_at = now
            await self.db.execute(
                delete(RecommendedPlace).where(
                    RecommendedPlace.generated_plan_id == plan.id
                )
            )

        places_to_add = [
            self._build_place(plan.id, place)
            for place in planner_response.recommended_places
        ]
        if places_to_add:
            self.db.add_all(places_to_add)

        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def mark_generation_requested(
        self, trip_vacancy_id: int, delete: bool = False
    ) -> GeneratedTripPlan:

        plan = await self.get_by_trip_vacancy_id(trip_vacancy_id)

        if delete and plan:
            await self.db.delete(plan)
            await self.db.commit()
            return plan
        if not plan:
            plan = GeneratedTripPlan(
                trip_vacancy_id=trip_vacancy_id,
                raw_response={},
                generation_requested_at=datetime.utcnow(),
                generated_at=None,
            )
            self.db.add(plan)
        else:
            plan.generation_requested_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    def _build_place(
        self, generated_plan_id: int, place: RecommendedPlaceSchema
    ) -> RecommendedPlace:
        return RecommendedPlace(
            generated_plan_id=generated_plan_id,
            place_id=place.place_id,
            name=place.name,
            category=place.category,
            latitude=Decimal(str(place.coordinates.latitude)),
            longitude=Decimal(str(place.coordinates.longitude)),
            address=place.address,
            city=place.city,
            country=place.country,
            short_description=place.short_description,
            why_people_go=place.why_people_go,
            why_recommended=place.why_recommended,
            highlights=place.highlights,
            tags=place.tags,
            best_season=place.best_season,
            audience=place.audience,
            estimated_cost=Decimal(str(place.estimated_cost)),
            ticket_price=Decimal(str(place.ticket_price)),
            visit_duration_minutes=place.visit_duration_minutes,
            best_time_of_day=place.best_time_of_day,
            rating=Decimal(str(place.rating)),
            reviews_count=place.reviews_count,
            image_url=place.image_url,
            opening_hours=place.opening_hours.model_dump(),
            contact_information=place.contact_information.model_dump(),
            age_range=place.age_range.model_dump(),
            raw_payload=place.model_dump(),
            query_to_search=place.query_to_search,
        )

    def _to_optional_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        value_str = str(value).strip()
        return value_str if value_str else None

    def _to_decimal(self, value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    def _to_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None
