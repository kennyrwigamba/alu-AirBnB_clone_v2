#!/usr/bin/python3
"""City model."""

import os

from models.base_model import Base, BaseModel

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, ForeignKey, String
    from sqlalchemy.orm import relationship


class City(BaseModel, Base):
    """Represent a city within a state."""

    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "cities"
        state_id = Column(
            String(60), ForeignKey("states.id"), nullable=False
        )
        name = Column(String(128), nullable=False)
    else:
        state_id = ""
        name = ""


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    City.places = relationship(
        "Place",
        backref="cities",
        cascade="all, delete, delete-orphan",
    )
