#!/usr/bin/python3
"""Base model shared by all application entities."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseModel:
    """Provide identity, timestamps, and serialization for a model."""

    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, *args, **kwargs):
        """Create a model from keyword data or default values."""
        now = datetime.utcnow()
        if "id" not in kwargs:
            self.id = str(uuid4())
        if "created_at" not in kwargs:
            self.created_at = now
        if "updated_at" not in kwargs:
            self.updated_at = now
        for key, value in kwargs.items():
            if key in ("created_at", "updated_at") and isinstance(
                value, str
            ):
                value = datetime.fromisoformat(value)
            if key != "__class__":
                setattr(self, key, value)

    def __str__(self):
        """Return a readable representation of the model."""
        return "[{}] ({}) {}".format(
            self.__class__.__name__, self.id, self.__dict__
        )

    def save(self):
        """Update the modification timestamp and persist the model."""
        self.updated_at = datetime.utcnow()
        from models import storage

        storage.new(self)
        storage.save()

    def to_dict(self):
        """Return a JSON-serializable dictionary representation."""
        result = self.__dict__.copy()
        result.pop("_sa_instance_state", None)
        result["__class__"] = self.__class__.__name__
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result

    def delete(self):
        """Delete this instance from the configured storage."""
        from models import storage

        storage.delete(self)
