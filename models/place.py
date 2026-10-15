#!/usr/bin/python3
"""Place model."""

import os

from models.base_model import Base, BaseModel

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table

if os.getenv("HBNB_TYPE_STORAGE") == "db":
    place_amenity = Table(
        "place_amenity",
        Base.metadata,
        Column(
            "place_id", String(60), ForeignKey("places.id"),
            primary_key=True, nullable=False,
        ),
        Column(
            "amenity_id", String(60), ForeignKey("amenities.id"),
            primary_key=True, nullable=False,
        ),
    )


class Place(BaseModel, Base):
    """Represent a property listed for booking."""

    amenity_ids = []
    if os.getenv("HBNB_TYPE_STORAGE") == "db":
        __tablename__ = "places"
        city_id = Column(String(60), ForeignKey("cities.id"), nullable=False)
        user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
        name = Column(String(128), nullable=False)
        description = Column(String(1024), nullable=True)
        number_rooms = Column(Integer, nullable=False, default=0)
        number_bathrooms = Column(Integer, nullable=False, default=0)
        max_guest = Column(Integer, nullable=False, default=0)
        price_by_night = Column(Integer, nullable=False, default=0)
        latitude = Column(Float, nullable=True)
        longitude = Column(Float, nullable=True)
    else:
        city_id = ""
        user_id = ""
        name = ""
        description = ""
        number_rooms = 0
        number_bathrooms = 0
        max_guest = 0
        price_by_night = 0
        latitude = 0.0
        longitude = 0.0

    def __init__(self, *args, **kwargs):
        """Initialize a place with its listing information."""
        super().__init__(*args, **kwargs)
        self.amenity_ids = list(getattr(self, "amenity_ids", []))


if os.getenv("HBNB_TYPE_STORAGE") == "db":
    from sqlalchemy.orm import relationship

    Place.amenities = relationship(
        "Amenity",
        secondary=place_amenity,
        viewonly=False,
        back_populates="place_amenities",
    )
    Place.reviews = relationship(
        "Review",
        backref="place",
        cascade="all, delete, delete-orphan",
    )
else:
    from models.amenity import Amenity

    @property
    def _amenities(self):
        from models import storage

        return [
            amenity for amenity in storage.all(Amenity).values()
            if amenity.id in self.amenity_ids
        ]

    @_amenities.setter
    def _amenities(self, obj):
        if isinstance(obj, Amenity) and obj.id not in self.amenity_ids:
            self.amenity_ids.append(obj.id)

    Place.amenities = _amenities
    Place.reviews = property(
        lambda self: [
            review for review in __import__("models").storage.all().values()
            if (review.__class__.__name__ == "Review" and
                review.place_id == self.id)
        ]
    )
