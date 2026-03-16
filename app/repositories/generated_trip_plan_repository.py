from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.generated_trip_plan import GeneratedTripPlan
from app.models.recommended_place import RecommendedPlace


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
        self, trip_vacancy_id: int, planner_response: Dict[str, Any]
    ) -> GeneratedTripPlan:
        plan = await self.get_by_trip_vacancy_id(trip_vacancy_id)

        if not plan:
            plan = GeneratedTripPlan(
                trip_vacancy_id=trip_vacancy_id,
                raw_response=planner_response,
                generation_requested_at=datetime.utcnow(),
                generated_at=datetime.utcnow(),
            )
            self.db.add(plan)
            await self.db.flush()
        else:
            plan.raw_response = planner_response
            if not plan.generation_requested_at:
                plan.generation_requested_at = datetime.utcnow()
            plan.generated_at = datetime.utcnow()
            await self.db.execute(
                delete(RecommendedPlace).where(
                    RecommendedPlace.generated_plan_id == plan.id
                )
            )

        recommended_places = planner_response.get("recommended_places", [])
        if isinstance(recommended_places, list):
            places_to_add = [
                self._build_place(plan.id, place)
                for place in recommended_places
                if isinstance(place, dict)
            ]
            if places_to_add:
                self.db.add_all(places_to_add)

        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def mark_generation_requested(self, trip_vacancy_id: int, delete: bool = False) -> GeneratedTripPlan:


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
        self, generated_plan_id: int, place: Dict[str, Any]
    ) -> RecommendedPlace:
        coordinates = place.get("coordinates") or {}

        return RecommendedPlace(
            generated_plan_id=generated_plan_id,
            place_id=str(place.get("place_id") or ""),
            name=str(place.get("name") or "Unknown place"),
            category=self._to_optional_str(place.get("category")),
            latitude=self._to_decimal(coordinates.get("latitude")),
            longitude=self._to_decimal(coordinates.get("longitude")),
            address=self._to_optional_str(place.get("address")),
            city=self._to_optional_str(place.get("city")),
            country=self._to_optional_str(place.get("country")),
            short_description=self._to_optional_str(place.get("short_description")),
            why_people_go=self._to_optional_str(place.get("why_people_go")),
            why_recommended=self._to_optional_str(place.get("why_recommended")),
            highlights=(
                place.get("highlights")
                if isinstance(place.get("highlights"), list)
                else None
            ),
            tags=place.get("tags") if isinstance(place.get("tags"), list) else None,
            best_season=(
                place.get("best_season")
                if isinstance(place.get("best_season"), list)
                else None
            ),
            audience=(
                place.get("audience")
                if isinstance(place.get("audience"), list)
                else None
            ),
            estimated_cost=self._to_decimal(place.get("estimated_cost")),
            ticket_price=self._to_decimal(place.get("ticket_price")),
            visit_duration_minutes=self._to_int(place.get("visit_duration_minutes")),
            best_time_of_day=self._to_optional_str(place.get("best_time_of_day")),
            rating=self._to_decimal(place.get("rating")),
            reviews_count=self._to_int(place.get("reviews_count")),
            image_url=self._to_optional_str(place.get("image_url")),
            opening_hours=(
                place.get("opening_hours")
                if isinstance(place.get("opening_hours"), dict)
                else None
            ),
            contact_information=(
                place.get("contact_information")
                if isinstance(place.get("contact_information"), dict)
                else None
            ),
            age_range=(
                place.get("age_range")
                if isinstance(place.get("age_range"), dict)
                else None
            ),
            raw_payload=place,
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
