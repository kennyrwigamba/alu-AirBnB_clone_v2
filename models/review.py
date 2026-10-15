#!/usr/bin/python3
"""Review model."""

from sqlalchemy import Column, ForeignKey, String

from models.base_model import Base, BaseModel


class Review(BaseModel, Base):
    """Represent a review written for a place."""

    __tablename__ = "reviews"
    place_id = Column(String(60), ForeignKey("places.id"), nullable=False)
    user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
    text = Column(String(1024), nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialize a review with its author, place, and text."""
        super().__init__(*args, **kwargs)
        if getattr(self, "place_id", None) is None:
            self.place_id = ""
        if getattr(self, "user_id", None) is None:
            self.user_id = ""
        if getattr(self, "text", None) is None:
            self.text = ""
