#!/usr/bin/python3
"""State model."""

import os

from sqlalchemy import Column, String
from sqlalchemy.orm import backref, relationship

from models.base_model import Base, BaseModel


class State(BaseModel, Base):
    """Represent a geographic state or region."""

    __tablename__ = "states"
    name = Column(String(128), nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialize a state with a name."""
        super().__init__(*args, **kwargs)
        if getattr(self, "name", None) is None:
            self.name = ""


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    State.cities = relationship(
        "City",
        backref=backref("state"),
        cascade="all, delete, delete-orphan",
    )
else:
    State.cities = property(
        lambda self: [
            city for city in __import__("models").storage.all().values()
            if (
                city.__class__.__name__ == "City" and
                city.state_id == self.id
            )
        ]
    )
