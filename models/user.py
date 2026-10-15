#!/usr/bin/python3
"""User model."""

import os

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


class User(BaseModel, Base):
    """Represent a user of the application."""

    __tablename__ = "users"
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)

    def __init__(self, *args, **kwargs):
        """Initialize a user with common account fields."""
        super().__init__(*args, **kwargs)


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    User.places = relationship(
        "Place",
        backref="user",
        cascade="all, delete, delete-orphan",
    )
    User.reviews = relationship(
        "Review",
        backref="user",
        cascade="all, delete, delete-orphan",
    )
