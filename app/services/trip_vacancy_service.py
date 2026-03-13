from datetime import date
import json
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_vacancy import TripVacancy
from app.repositories.trip_vacancy_repository import TripVacancyRepository
from app.repositories.chat_group_repository import ChatGroupRepository
from app.repositories.chat_member_repository import ChatMemberRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.profile_repository import ProfileRepository


class TripVacancyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.trip_vacancy_repo = TripVacancyRepository(db)
        self.chat_group_repo = ChatGroupRepository(db)
        self.chat_member_repo = ChatMemberRepository(db)
        self.offer_repo = OfferRepository(db)
        self.profile_repo = ProfileRepository(db)

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

            # Create chat group for the trip vacancy
            destination_city = trip_vacancy_data.get("destination_city", "Trip")
            chat_group_name = f"Trip to {destination_city}"
            chat_group = await self.chat_group_repo.create(
                trip_vacancy.id, chat_group_name
            )

            # Add the requester as the first member
            await self.chat_member_repo.create(chat_group.id, requester_id)

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
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        gender_preference: Optional[str] = None,
        from_city: Optional[str] = None,
        from_country: Optional[str] = None,
    ) -> List[TripVacancy]:
        """Get all trip vacancies with optional filters. Defaults to showing only 'open' vacancies."""
        # Default to showing only 'open' vacancies if no status filter is provided
        if status is None:
            status = "open"

        return await self.trip_vacancy_repo.get_all(
            skip=skip,
            limit=limit,
            destination_city=destination_city,
            destination_country=destination_country,
            status=status,
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

    # ============= GENERATE PLAN =============
    async def generate_plan(
        self, trip_vacancy_id: int, user_id: int
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Collect tripmates data and save it to a local JSON file."""
        try:
            # Get trip vacancy
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)
            if not trip_vacancy:
                return False, None, "Trip vacancy not found"

            # Check if user has access (must be requester or accepted offerer)
            if trip_vacancy.requester_id != user_id:
                # Check if user is an accepted offerer
                offer = await self.offer_repo.check_existing_offer(
                    trip_vacancy_id, user_id
                )
                if not offer or offer.status != "accepted":
                    return (
                        False,
                        None,
                        "You don't have permission to generate plan for this trip",
                    )

            # Check if trip vacancy is full
            if trip_vacancy.people_joined < trip_vacancy.people_needed:
                return (
                    False,
                    None,
                    f"Trip vacancy is not full yet. Currently {trip_vacancy.people_joined}/{trip_vacancy.people_needed} people joined",
                )

            # Get all accepted offers for this trip
            accepted_offers = await self.offer_repo.get_offers_by_status(
                trip_vacancy_id, "accepted", skip=0, limit=100
            )

            # Fetch all related profiles in one query to avoid N+1 selects
            profile_user_ids = [trip_vacancy.requester_id] + [
                offer.offerer_id for offer in accepted_offers
            ]
            profiles = await self.profile_repo.get_by_user_ids_with_relations(
                profile_user_ids
            )
            profiles_by_user_id = {profile.user_id: profile for profile in profiles}

            # Collect all user data
            users_data = []

            # Add requester as user-1
            requester_profile = profiles_by_user_id.get(trip_vacancy.requester_id)
            if requester_profile:
                users_data.append(
                    {
                        "user_label": requester_profile.first_name + " " + requester_profile.last_name,
                        "age": self._calculate_age(requester_profile.date_of_birth),
                        "gender": requester_profile.gender,
                        "interests": [
                            ui.interest.name for ui in requester_profile.interests
                        ],
                        "travel_styles": [
                            ts.travel_style.name
                            for ts in requester_profile.travel_styles
                        ],
                    }
                )

            # Add accepted offerers as user-2, user-3, etc.
            for idx, offer in enumerate(accepted_offers, start=2):
                offerer_profile = profiles_by_user_id.get(offer.offerer_id)
                if offerer_profile:
                    users_data.append(
                        {
                            "user_label": offerer_profile.first_name + " " + offerer_profile.last_name,
                            "age": self._calculate_age(offerer_profile.date_of_birth),
                            "gender": offerer_profile.gender,
                            "interests": [
                                ui.interest.name for ui in offerer_profile.interests
                            ],
                            "travel_styles": [
                                ts.travel_style.name
                                for ts in offerer_profile.travel_styles
                            ],
                        }
                    )

            output_file = await self._save_users_data_to_json(trip_vacancy, users_data)

            return True, f"User information saved to {output_file}", None

        except Exception as e:
            return False, None, f"Failed to generate plan: {str(e)}"

    def _calculate_age(self, date_of_birth: date) -> int:
        """Calculate age from date of birth."""
        from datetime import date as dt_date

        today = dt_date.today()
        return (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )

    async def _save_users_data_to_json(
        self, trip_vacancy: TripVacancy, users_data: List[dict]
    ) -> str:
        """Save tripmates information to a local JSON file without external calls."""
        payload = {
            "trip_vacancy_id": trip_vacancy.id,
            "destination_city": trip_vacancy.destination_city,
            "destination_country": trip_vacancy.destination_country,
            "start_date": trip_vacancy.start_date.isoformat()
            if trip_vacancy.start_date
            else None,
            "end_date": trip_vacancy.end_date.isoformat()
            if trip_vacancy.end_date
            else None,
            "users": users_data,
        }

        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / "generated_plans"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"trip_{trip_vacancy.id}_users.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return str(output_file)
