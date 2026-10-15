#!/usr/bin/python3
"""Amenity model."""

import os

from models.base_model import Base, BaseModel

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, String


class Amenity(BaseModel, Base):
    """Represent an amenity available at a place."""

    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "amenities"
        name = Column(String(128), nullable=False)
    else:
        name = ""


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy.orm import relationship

    Amenity.place_amenities = relationship(
        "Place",
        secondary="place_amenity",
        viewonly=False,
        back_populates="amenities",
    )
