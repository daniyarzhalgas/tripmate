from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ============= Request Schemas =============
class OfferCreateRequest(BaseModel):
    trip_vacancy_id: int = Field(..., gt=0)
    message: Optional[str] = Field(None, max_length=2000)
    proposed_budget: Optional[Decimal] = Field(None, ge=0)


class OfferUpdateRequest(BaseModel):
    message: Optional[str] = Field(None, max_length=2000)
    proposed_budget: Optional[Decimal] = Field(None, ge=0)


class OfferStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(accepted|rejected|cancelled)$")


# ============= Response Schemas =============
class OfferResponse(BaseModel):
    id: int
    trip_vacancy_id: int
    offerer_id: int
    message: Optional[str]
    proposed_budget: Optional[Decimal]
    status: str
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Message Response =============
class MessageResponse(BaseModel):
    message: str
