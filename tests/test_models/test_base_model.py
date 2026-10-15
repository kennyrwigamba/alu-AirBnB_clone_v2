#!/usr/bin/python3
"""Validate identity, timestamps, serialization, and model persistence."""

from datetime import datetime, timedelta
import json
import unittest
from unittest.mock import patch
from uuid import UUID

from models import storage
from models.base_model import BaseModel
from tests.storage_test_case import DB_STORAGE, StorageTestCase


class TestBaseModel(StorageTestCase):
    """Exercise common behavior for BaseModel and each derived model."""

    model_class = BaseModel
    defaults = {}

    def test_identity(self):
        """New instances have distinct string UUIDs of version four."""
        first, second = self.model_class(), self.model_class()
        self.assertIsInstance(first.id, str)
        self.assertEqual(UUID(first.id).version, 4)
        self.assertNotEqual(first.id, second.id)

    def test_timestamps(self):
        """New timestamps are datetime values within construction time."""
        before = datetime.utcnow()
        model = self.model_class()
        after = datetime.utcnow()
        for value in (model.created_at, model.updated_at):
            self.assertIsInstance(value, datetime)
            self.assertLessEqual(before, value)
            self.assertLessEqual(value, after)

    def test_registration(self):
        """New models are registered when saved, not when constructed."""
        with patch.object(storage, "new") as new:
            model = self.model_class()
            new.assert_not_called()
            with patch.object(storage, "save"):
                model.save()
            new.assert_called_once_with(model)

    def test_args_ignored(self):
        """Positional arguments do not become model attributes."""
        model = self.model_class("ignored", 42)
        self.assertNotEqual(model.id, "ignored")
        self.assertIsInstance(model.created_at, datetime)

    def test_string(self):
        """String output includes the exact class, ID, and attributes."""
        model = self.model_class()
        expected = "[{}] ({}) {}".format(
            self.model_class.__name__, model.id, model.__dict__
        )
        self.assertEqual(str(model), expected)

    def test_dictionary(self):
        """Serialization includes custom data and ISO-format timestamps."""
        model = self.model_class()
        model.custom_number = 89
        data = model.to_dict()
        expected = model.__dict__.copy()
        expected.pop("_sa_instance_state", None)
        expected.update({
            "__class__": self.model_class.__name__,
            "created_at": model.created_at.isoformat(),
            "updated_at": model.updated_at.isoformat(),
        })
        self.assertEqual(data, expected)
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_dictionary_does_not_mutate_model(self):
        """Serialization leaves the model's timestamps and dict intact."""
        model = self.model_class()
        original = model.__dict__.copy()
        data = model.to_dict()
        data["id"] = "different"
        self.assertEqual(model.__dict__, original)
        self.assertNotIn("__class__", model.__dict__)

    def test_dictionary_reconstruction(self):
        """Keyword data restores identity, custom fields, and datetimes."""
        model = self.model_class()
        model.custom_text = "Restored value"
        restored = self.model_class(**model.to_dict())
        self.assertIsNot(restored, model)
        self.assertEqual(restored.to_dict(), model.to_dict())
        self.assertNotIn("__class__", restored.__dict__)

    def test_reconstruction_does_not_register(self):
        """Dictionary construction does not register a new object."""
        data = self.model_class().to_dict()
        with patch.object(storage, "new") as new:
            self.model_class(**data)
        new.assert_not_called()

    def test_save(self):
        """Saving advances updated_at and registers before committing."""
        model = self.model_class()
        created = model.created_at
        later = model.updated_at + timedelta(seconds=1)
        with patch("models.base_model.datetime") as clock, \
                patch.object(storage, "new") as new, \
                patch.object(storage, "save") as save:
            clock.utcnow.return_value = later
            model.save()
        new.assert_called_once_with(model)
        save.assert_called_once_with()
        self.assertEqual(model.updated_at, later)
        self.assertEqual(model.created_at, created)

    @unittest.skipIf(DB_STORAGE, "SQL columns replace file defaults")
    def test_defaults_and_inheritance(self):
        """Derived models inherit BaseModel and declare typed defaults."""
        model = self.model_class()
        self.assertIsInstance(model, BaseModel)
        for name, expected in self.defaults.items():
            self.assertEqual(getattr(self.model_class, name), expected)
            self.assertEqual(getattr(model, name), expected)
            self.assertIs(type(getattr(model, name)), type(expected))

    def test_keyword_attributes(self):
        """Keyword reconstruction preserves overridden model fields."""
        data = self.model_class().to_dict()
        for name, default in self.defaults.items():
            if isinstance(default, str):
                data[name] = "custom"
            elif isinstance(default, list):
                data[name] = ["amenity-id"]
            elif isinstance(default, int):
                data[name] = 3
            else:
                data[name] = 1.5
        restored = self.model_class(**data)
        self.assertEqual(restored.to_dict(), data)

    def test_delete(self):
        """Deletion delegates the instance to the selected storage."""
        model = self.model_class()
        with patch.object(storage, "delete") as delete:
            model.delete()
        delete.assert_called_once_with(model)

    def test_dictionary_hides_sqlalchemy_state(self):
        """SQLAlchemy instrumentation is absent from serialized data."""
        model = self.model_class()
        self.assertNotIn("_sa_instance_state", model.to_dict())

    def test_missing_keyword_timestamps(self):
        """Partial keyword data receives fresh identity and timestamps."""
        model = self.model_class(custom_text="value")
        self.assertIsInstance(model.id, str)
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)
        self.assertEqual(model.custom_text, "value")

    def test_timestamps_without_microseconds(self):
        """ISO timestamps with whole seconds deserialize correctly."""
        value = "2017-03-25T19:42:40"
        model = self.model_class(created_at=value, updated_at=value)
        expected = datetime(2017, 3, 25, 19, 42, 40)
        self.assertEqual(model.created_at, expected)
        self.assertEqual(model.updated_at, expected)
        restored = self.model_class(**model.to_dict())
        self.assertEqual(restored.to_dict(), model.to_dict())
