import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class TravelStyleEnum(str, enum.Enum):
    solo = "solo"
    group = "group"
    adventure = "adventure"
    luxury = "luxury"
    historical = "historical"


    
