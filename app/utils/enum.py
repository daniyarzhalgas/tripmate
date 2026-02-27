import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

    
