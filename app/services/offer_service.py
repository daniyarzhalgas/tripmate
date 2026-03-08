from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer
from app.repositories.offer_repository import OfferRepository
from app.repositories.trip_vacancy_repository import TripVacancyRepository
from app.repositories.chat_group_repository import ChatGroupRepository
from app.repositories.chat_member_repository import ChatMemberRepository


class OfferService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.offer_repo = OfferRepository(db)
        self.trip_vacancy_repo = TripVacancyRepository(db)
        self.chat_group_repo = ChatGroupRepository(db)
        self.chat_member_repo = ChatMemberRepository(db)

    # ============= CREATE =============
    async def create_offer(
        self, offerer_id: int, **offer_data
    ) -> Tuple[bool, Optional[Offer], Optional[str]]:
        """Create a new offer for a trip vacancy."""
        try:
            trip_vacancy_id = offer_data.get("trip_vacancy_id")

            # Check if trip vacancy exists
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)
            if not trip_vacancy:
                return False, None, "Trip vacancy not found"

            # Check if trip vacancy is active
            if trip_vacancy.status != "open":
                return False, None, "Trip vacancy is not active"

            # Check if user is the requester of the trip vacancy
            if trip_vacancy.requester_id == offerer_id:
                return False, None, "You cannot make an offer for your own trip vacancy"

            # Check if user already made an offer
            existing_offer = await self.offer_repo.check_existing_offer(
                trip_vacancy_id, offerer_id
            )
            if existing_offer:
                return (
                    False,
                    None,
                    "You already have an active offer for this trip vacancy",
                )

            # Create the offer
            offer = await self.offer_repo.create(offerer_id=offerer_id, **offer_data)
            return True, offer, None

        except Exception as e:
            return False, None, f"Failed to create offer: {str(e)}"

    # ============= READ =============
    async def get_offer_by_id(
        self, offer_id: int, user_id: int
    ) -> Tuple[bool, Optional[Offer], Optional[str]]:
        """Get an offer by ID. User must be either the offerer or the trip vacancy requester."""
        try:
            offer = await self.offer_repo.get_by_id(offer_id)
            if not offer:
                return False, None, "Offer not found"

            # Get trip vacancy to check if user is the requester
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(offer.trip_vacancy_id)

            # Check if user has access to this offer
            if offer.offerer_id != user_id and trip_vacancy.requester_id != user_id:
                return False, None, "You don't have permission to view this offer"

            return True, offer, None

        except Exception as e:
            return False, None, f"Failed to get offer: {str(e)}"

    async def get_my_offers(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Offer]:
        """Get all offers made by the current user."""
        return await self.offer_repo.get_by_offerer_id(user_id, skip, limit)

    async def get_offers_for_trip_vacancy(
        self,
        trip_vacancy_id: int,
        requester_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[bool, Optional[List[Offer]], Optional[str]]:
        """Get all offers for a trip vacancy. Only the requester can view them."""
        try:
            # Check if trip vacancy exists and user is the requester
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(trip_vacancy_id)
            if not trip_vacancy:
                return False, None, "Trip vacancy not found"

            if trip_vacancy.requester_id != requester_id:
                return (
                    False,
                    None,
                    "You don't have permission to view offers for this trip vacancy",
                )

            # Get offers
            if status:
                offers = await self.offer_repo.get_offers_by_status(
                    trip_vacancy_id, status, skip, limit
                )
            else:
                offers = await self.offer_repo.get_by_trip_vacancy_id(
                    trip_vacancy_id, skip, limit
                )

            return True, offers, None

        except Exception as e:
            return False, None, f"Failed to get offers: {str(e)}"

    # ============= UPDATE =============
    async def update_offer(
        self, offer_id: int, offerer_id: int, **update_data
    ) -> Tuple[bool, Optional[Offer], Optional[str]]:
        """Update an offer. Only the offerer can update it and only if it's pending."""
        try:
            offer = await self.offer_repo.get_by_id(offer_id)
            if not offer:
                return False, None, "Offer not found"

            # Check if user is the offerer
            if offer.offerer_id != offerer_id:
                return False, None, "You don't have permission to update this offer"

            # Can only update pending offers
            if offer.status != "pending":
                return False, None, "You can only update pending offers"

            # Update the offer
            updated_offer = await self.offer_repo.update(offer, **update_data)
            return True, updated_offer, None

        except Exception as e:
            return False, None, f"Failed to update offer: {str(e)}"

    async def update_offer_status(
        self, offer_id: int, requester_id: int, new_status: str
    ) -> Tuple[bool, Optional[Offer], Optional[str]]:
        """Update offer status. Only the trip vacancy requester can accept/reject offers."""
        try:
            offer = await self.offer_repo.get_by_id(offer_id)
            if not offer:
                return False, None, "Offer not found"

            # Get trip vacancy
            trip_vacancy = await self.trip_vacancy_repo.get_by_id(offer.trip_vacancy_id)
            if not trip_vacancy:
                return False, None, "Trip vacancy not found"

            # Check if user is the requester
            if trip_vacancy.requester_id != requester_id:
                return (
                    False,
                    None,
                    "Only the trip vacancy requester can change offer status",
                )

            # Can only accept/reject pending offers
            if offer.status != "pending":
                return False, None, "Only pending offers can be accepted or rejected"

            # Validate status
            if new_status not in ["accepted", "rejected"]:
                return False, None, "Invalid status. Use 'accepted' or 'rejected'"

            # If accepting offer, update trip vacancy and add user to chat
            if new_status == "accepted":
                # Check if vacancy is full
                if trip_vacancy.people_joined >= trip_vacancy.people_needed:
                    return False, None, "Trip vacancy is already full"

                # Increment people_joined
                new_people_joined = trip_vacancy.people_joined + 1
                
                # Determine new status for trip vacancy
                new_vacancy_status = trip_vacancy.status
                if new_people_joined >= trip_vacancy.people_needed:
                    new_vacancy_status = "matched"
                
                # Update trip vacancy
                await self.trip_vacancy_repo.update(
                    trip_vacancy.id, 
                    people_joined=new_people_joined,
                    status=new_vacancy_status
                )

                # Add the offerer to the chat group
                chat_group = await self.chat_group_repo.get_by_trip_vacancy_id(
                    trip_vacancy.id
                )
                if chat_group:
                    # Check if user is not already a member
                    is_member = await self.chat_member_repo.is_member(
                        chat_group.id, offer.offerer_id
                    )
                    if not is_member:
                        await self.chat_member_repo.create(
                            chat_group.id, offer.offerer_id
                        )

            # Update offer status
            updated_offer = await self.offer_repo.update_status(
                offer, new_status, reviewed_at=datetime.utcnow()
            )
            return True, updated_offer, None

        except Exception as e:
            return False, None, f"Failed to update offer status: {str(e)}"

    async def cancel_offer(
        self, offer_id: int, offerer_id: int
    ) -> Tuple[bool, Optional[Offer], Optional[str]]:
        """Cancel an offer. Only the offerer can cancel their own offer."""
        try:
            offer = await self.offer_repo.get_by_id(offer_id)
            if not offer:
                return False, None, "Offer not found"

            # Check if user is the offerer
            if offer.offerer_id != offerer_id:
                return False, None, "You don't have permission to cancel this offer"

            # Can only cancel pending offers
            if offer.status != "pending":
                return False, None, "You can only cancel pending offers"

            # Cancel the offer
            updated_offer = await self.offer_repo.update_status(
                offer, "cancelled", reviewed_at=datetime.utcnow()
            )
            return True, updated_offer, None

        except Exception as e:
            return False, None, f"Failed to cancel offer: {str(e)}"

    # ============= DELETE =============
    async def delete_offer(
        self, offer_id: int, user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Delete an offer. Only the offerer can delete their own offer."""
        try:
            offer = await self.offer_repo.get_by_id(offer_id)
            if not offer:
                return False, "Offer not found"

            # Check if user is the offerer
            if offer.offerer_id != user_id:
                return False, "You don't have permission to delete this offer"

            # Can only delete cancelled or rejected offers
            if offer.status not in ["cancelled", "rejected"]:
                return False, "You can only delete cancelled or rejected offers"

            await self.offer_repo.delete(offer)
            return True, None

        except Exception as e:
            return False, f"Failed to delete offer: {str(e)}"
