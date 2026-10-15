#!/usr/bin/python3
"""User model."""

import os

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, String
    from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel


class User(BaseModel, Base):
    """Represent a user of the application."""

    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "users"
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""


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
