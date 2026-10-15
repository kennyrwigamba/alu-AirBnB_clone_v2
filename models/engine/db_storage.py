#!/usr/bin/python3
"""SQLAlchemy database storage engine."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.amenity import Amenity
from models.base_model import Base
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class DBStorage:
    """Persist application models in a MySQL database."""

    __engine = None
    __session = None

    def __init__(self):
        """Create the database engine from environment configuration."""
        user = os.getenv("HBNB_MYSQL_USER")
        password = os.getenv("HBNB_MYSQL_PWD")
        host = os.getenv("HBNB_MYSQL_HOST")
        database = os.getenv("HBNB_MYSQL_DB")
        url = "mysql+mysqldb://{}:{}@{}/{}".format(
            user, password, host, database
        )
        self.__engine = create_engine(url, pool_pre_ping=True)

    def all(self, cls=None):
        """Return all database objects, optionally filtered by class."""
        classes = (User, State, City, Amenity, Place, Review)
        if cls is not None:
            classes = (cls,)
        objects = {}
        for model_class in classes:
            for model in self.__session.query(model_class).all():
                key = "{}.{}".format(
                    model.__class__.__name__, model.id
                )
                objects[key] = model
        return objects

    def new(self, obj):
        """Add an object to the current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit the current database session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete an object from the current database session."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create tables and initialize a thread-safe database session."""
        if os.getenv("HBNB_ENV") == "test":
            Base.metadata.drop_all(self.__engine)
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(
            bind=self.__engine,
            expire_on_commit=False,
        )
        self.__session = scoped_session(factory)

    def close(self):
        """Remove the current scoped database session."""
        self.__session.remove()
