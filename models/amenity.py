#!/usr/bin/python3
"""Amenity model."""

import os

from sqlalchemy import Column, String

from models.base_model import Base, BaseModel


class Amenity(BaseModel, Base):
    """Represent an amenity available at a place."""

    __tablename__ = "amenities"
    name = Column(String(128), nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialize an amenity with a name."""
        super().__init__(*args, **kwargs)
        if getattr(self, "name", None) is None:
            self.name = ""


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy.orm import relationship

    Amenity.place_amenities = relationship(
        "Place",
        secondary="place_amenity",
        viewonly=False,
        back_populates="amenities",
    )
