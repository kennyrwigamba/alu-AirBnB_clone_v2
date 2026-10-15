#!/usr/bin/python3
"""State model."""

import os

from models.base_model import Base, BaseModel

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, String
    from sqlalchemy.orm import relationship


class State(BaseModel, Base):
    """Represent a geographic state or region."""

    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "states"
        name = Column(String(128), nullable=False)
        cities = relationship(
            "City", backref="state", cascade="all, delete, delete-orphan",
        )
    else:
        name = ""

        @property
        def cities(self):
            """Return saved cities whose state_id matches this state."""
            from models import storage
            from models.city import City

            return [city for city in storage.all(City).values()
                    if city.state_id == self.id]
