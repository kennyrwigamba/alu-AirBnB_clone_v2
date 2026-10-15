#!/usr/bin/python3
"""Review model."""

import os

from models.base_model import Base, BaseModel

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, ForeignKey, String


class Review(BaseModel, Base):
    """Represent a review written for a place."""

    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "reviews"
        place_id = Column(String(60), ForeignKey("places.id"), nullable=False)
        user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
        text = Column(String(1024), nullable=False)
    else:
        place_id = ""
        user_id = ""
        text = ""
