from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country_id = Column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    country = relationship("Country", back_populates="cities")
