#!/usr/bin/python3
"""JSON file storage engine."""

import json
import os

from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class FileStorage:
    """Serialize and restore models from a JSON file."""

    __file_path = "file.json"
    __objects = {}
    __classes = {
        "Amenity": Amenity,
        "BaseModel": BaseModel,
        "City": City,
        "Place": Place,
        "Review": Review,
        "State": State,
        "User": User,
    }

    def all(self, cls=None):
        """Return all stored objects, optionally filtered by class."""
        if cls is None:
            return self.__objects
        if isinstance(cls, str):
            cls = self.__classes.get(cls)
            if cls is None:
                return {}
        return {
            key: value for key, value in self.__objects.items()
            if isinstance(value, cls)
        }

    def new(self, obj):
        """Add an object to storage."""
        key = "{}.{}".format(obj.__class__.__name__, obj.id)
        self.__objects[key] = obj

    def delete(self, obj=None):
        """Remove an object from storage if it is present."""
        if obj is None:
            return
        key = "{}.{}".format(obj.__class__.__name__, obj.id)
        self.__objects.pop(key, None)

    def save(self):
        """Write all stored objects to the JSON file."""
        data = {key: value.to_dict() for key, value in self.__objects.items()}
        with open(self.__file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def reload(self):
        """Load stored objects when the JSON file exists."""
        if not os.path.exists(self.__file_path):
            return

        with open(self.__file_path, encoding="utf-8") as file:
            data = json.load(file)
        for key, attributes in data.items():
            class_name = key.split(".")[0]
            model_class = self.__classes.get(class_name)
            if model_class is not None:
                self.__objects[key] = model_class(**attributes)

    def close(self):
        """Reload objects from the JSON file."""
        self.reload()
