from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai

from app.models.trip_vacancy import TripVacancy
from app.repositories.trip_vacancy_repository import TripVacancyRepository
from app.repositories.chat_group_repository import ChatGroupRepository
from app.repositories.chat_member_repository import ChatMemberRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.profile_repository import ProfileRepository
from app.core.config import config


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
        """Generate a travel plan using Gemini AI for a trip vacancy that is full."""
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

            # Get requester profile with relations
            requester_profile = await self.profile_repo.get_by_user_id_with_relations(
                trip_vacancy.requester_id
            )

            # Collect all user data
            users_data = []

            # Add requester as user-1
            if requester_profile:
                users_data.append(
                    {
                        "user_label": "user-1",
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
                offerer_profile = await self.profile_repo.get_by_user_id_with_relations(
                    offer.offerer_id
                )
                if offerer_profile:
                    users_data.append(
                        {
                            "user_label": f"user-{idx}",
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

            # Generate plan using Gemini AI
            plan = await self._generate_plan_with_gemini(trip_vacancy, users_data)

            return True, plan, None

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

    async def _generate_plan_with_gemini(
        self, trip_vacancy: TripVacancy, users_data: List[dict]
    ) -> str:
        """Call Gemini AI to generate a travel plan."""
        # Configure Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Format trip information
        trip_info = f"""
Trip Details:
- Destination: {trip_vacancy.destination_city}, {trip_vacancy.destination_country}
- Start Date: {trip_vacancy.start_date.strftime('%Y-%m-%d')}
- End Date: {trip_vacancy.end_date.strftime('%Y-%m-%d')}
- Duration: {(trip_vacancy.end_date - trip_vacancy.start_date).days} days
- Total People: {len(users_data)}
- Budget Range: ${trip_vacancy.min_budget or 'N/A'} - ${trip_vacancy.max_budget or 'N/A'}
- Description: {trip_vacancy.description or 'N/A'}
- Planned Activities: {trip_vacancy.planned_activities or 'N/A'}
- Planned Destinations: {trip_vacancy.planned_destinations or 'N/A'}
- Transportation Preference: {trip_vacancy.transportation_preference or 'N/A'}
- Accommodation Preference: {trip_vacancy.accommodation_preference or 'N/A'}

Tripmates Information:
"""

        # Add user information
        for user_data in users_data:
            trip_info += f"""
{user_data['user_label'].upper()}:
- Age: {user_data['age']}
- Gender: {user_data['gender']}
- Interests: {', '.join(user_data['interests']) if user_data['interests'] else 'None specified'}
- Travel Styles: {', '.join(user_data['travel_styles']) if user_data['travel_styles'] else 'None specified'}
"""

        prompt = f"""You are a travel planning assistant. Based on the following trip information and tripmates' preferences, generate a detailed day-by-day travel plan.

{trip_info}

Please create a comprehensive travel plan that:
1. Includes a day-by-day itinerary
2. Considers all tripmates' interests and travel styles
3. Balances activities to accommodate everyone's preferences
4. Suggests specific places, activities, and experiences
5. Includes practical information like meal suggestions and transportation
6. Stays within the budget range if specified
7. Considers accommodation preferences
8. Makes the trip enjoyable for all participants

Generate a well-structured travel plan:"""

        # Generate content
        response = model.generate_content(prompt)
        return response.text
