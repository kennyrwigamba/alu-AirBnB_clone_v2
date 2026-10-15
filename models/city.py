#!/usr/bin/python3
"""City model."""

import os

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


class City(BaseModel, Base):
    """Represent a city within a state."""

    __tablename__ = "cities"
    state_id = Column(
        String(60), ForeignKey("states.id"), nullable=False
    )
    name = Column(String(128), nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialize a city with its state and name."""
        super().__init__(*args, **kwargs)
        if getattr(self, "state_id", None) is None:
            self.state_id = ""
        if getattr(self, "name", None) is None:
            self.name = ""


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    City.places = relationship(
        "Place",
        backref="cities",
        cascade="all, delete, delete-orphan",
    )
