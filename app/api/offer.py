from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.offer import (
    MessageResponse,
    OfferCreateRequest,
    OfferResponse,
    OfferStatusUpdateRequest,
    OfferUpdateRequest,
)
from app.services.offer_service import OfferService

router = APIRouter(prefix="/offers", tags=["Offers"])


# ============= OFFER CRUD =============
@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    request: OfferCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new offer for a trip vacancy."""
    offer_service = OfferService(db)

    success, offer, error = await offer_service.create_offer(
        offerer_id=current_user.id, **request.model_dump()
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return offer


@router.get("/me", response_model=List[OfferResponse])
async def get_my_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all offers made by the current user."""
    offer_service = OfferService(db)
    offers = await offer_service.get_my_offers(current_user.id, skip, limit)
    return offers


@router.get("/trip-vacancy/{trip_vacancy_id}", response_model=List[OfferResponse])
async def get_offers_for_trip_vacancy(
    trip_vacancy_id: int,
    status: Optional[str] = Query(
        None, regex="^(pending|accepted|rejected|cancelled)$"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all offers for a specific trip vacancy. Only the requester can view them."""
    offer_service = OfferService(db)

    success, offers, error = await offer_service.get_offers_for_trip_vacancy(
        trip_vacancy_id=trip_vacancy_id,
        requester_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error,
        )

    return offers


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get an offer by ID. User must be either the offerer or the trip vacancy requester."""
    offer_service = OfferService(db)

    success, offer, error = await offer_service.get_offer_by_id(
        offer_id, current_user.id
    )

    if not success:
        if error == "Offer not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error,
            )

    return offer


@router.patch("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    request: OfferUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an offer. Only the offerer can update it and only if it's pending."""
    offer_service = OfferService(db)

    # Filter out None values
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    success, offer, error = await offer_service.update_offer(
        offer_id=offer_id, offerer_id=current_user.id, **update_data
    )

    if not success:
        if error == "Offer not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error,
            )

    return offer


@router.patch("/{offer_id}/status", response_model=OfferResponse)
async def update_offer_status(
    offer_id: int,
    request: OfferStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update offer status (accept/reject). Only the trip vacancy requester can do this."""
    offer_service = OfferService(db)

    success, offer, error = await offer_service.update_offer_status(
        offer_id=offer_id, requester_id=current_user.id, new_status=request.status
    )

    if not success:
        if error == "Offer not found" or error == "Trip vacancy not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error,
            )

    return offer


@router.post("/{offer_id}/cancel", response_model=OfferResponse)
async def cancel_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an offer. Only the offerer can cancel their own pending offer."""
    offer_service = OfferService(db)

    success, offer, error = await offer_service.cancel_offer(
        offer_id=offer_id, offerer_id=current_user.id
    )

    if not success:
        if error == "Offer not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error,
            )

    return offer


@router.delete("/{offer_id}", response_model=MessageResponse)
async def delete_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an offer. Only the offerer can delete their own cancelled or rejected offer."""
    offer_service = OfferService(db)

    success, error = await offer_service.delete_offer(offer_id, current_user.id)

    if not success:
        if error == "Offer not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error,
            )

    return MessageResponse(message="Offer deleted successfully")
