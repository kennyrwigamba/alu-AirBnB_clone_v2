#!/usr/bin/python3
"""Validate database persistence, mappings, and cascading relationships."""

import unittest
from unittest.mock import patch

from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from tests.storage_test_case import DB_STORAGE, StorageTestCase

if DB_STORAGE:
    from models.engine.db_storage import DBStorage


@unittest.skipUnless(DB_STORAGE, "DBStorage tests require database storage")
class TestDBStorage(StorageTestCase):
    """Run database checks inside a transaction rolled back after each test."""

    def setUp(self):
        """Create a valid graph with all required foreign keys."""
        super().setUp()
        self.state = State(name="California")
        self.user = User(email="test@example.com", password="test-password")
        self.city = City(name="San Francisco", state_id=self.state.id)
        self.place = Place(
            name="House", city_id=self.city.id, user_id=self.user.id,
        )
        self.review = Review(
            text="Great stay", place_id=self.place.id, user_id=self.user.id,
        )
        self.amenity = Amenity(name="Wifi")
        for obj in (self.state, self.user, self.city, self.place,
                    self.review, self.amenity):
            storage.new(obj)
        storage.save()

    def count_rows(self, table):
        """Count database rows directly through DB-API, without ORM queries."""
        cursor = self.connection.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM " + table)
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def test_selected_storage(self):
        """The environment selects the DBStorage implementation."""
        self.assertIsInstance(storage, DBStorage)

    def test_constructor_configuration(self):
        """Connection settings come from the MySQL environment variables."""
        settings = {
            "HBNB_MYSQL_USER": "test_user",
            "HBNB_MYSQL_PWD": "test_password",
            "HBNB_MYSQL_HOST": "localhost",
            "HBNB_MYSQL_DB": "test_database",
            "HBNB_ENV": "dev",
        }
        with patch.dict("os.environ", settings), \
                patch("models.engine.db_storage.create_engine") as create, \
                patch("models.engine.db_storage.Base.metadata") as metadata:
            engine_storage = DBStorage()
        create.assert_called_once_with(
            "mysql+mysqldb://test_user:test_password@localhost/test_database",
            pool_pre_ping=True,
        )
        metadata.drop_all.assert_not_called()
        self.assertIs(engine_storage._DBStorage__engine, create.return_value)

    def test_constructor_resets_test_database(self):
        """Only test mode requests table removal when creating an engine."""
        with patch.dict("os.environ", {"HBNB_ENV": "test"}), \
                patch("models.engine.db_storage.create_engine") as create, \
                patch("models.engine.db_storage.Base.metadata") as metadata:
            DBStorage()
        metadata.drop_all.assert_called_once_with(create.return_value)

    def test_primary_keys_and_foreign_keys(self):
        """Tables declare UUID primary keys and the required foreign keys."""
        for model in (State, City, User, Place, Review, Amenity):
            with self.subTest(model=model.__name__):
                column = model.__table__.c.id
                self.assertTrue(column.primary_key)
                self.assertFalse(column.nullable)
                self.assertEqual(column.type.length, 60)
        for model, attribute, target in (
            (City, "state_id", "states.id"),
            (Place, "city_id", "cities.id"),
            (Place, "user_id", "users.id"),
            (Review, "place_id", "places.id"),
            (Review, "user_id", "users.id"),
        ):
            column = model.__table__.c[attribute]
            self.assertFalse(column.nullable)
            self.assertEqual(
                {key.target_fullname for key in column.foreign_keys}, {target}
            )

    def test_new_and_save(self):
        """New and save insert a row visible to an independent SQL query."""
        before = self.count_rows("states")
        state = State(name="Nevada")
        storage.new(state)
        storage.save()
        self.assertEqual(self.count_rows("states"), before + 1)

    def test_all(self):
        """All returns each model indexed by its class name and ID."""
        objects = storage.all()
        for obj in (self.state, self.user, self.city, self.place,
                    self.review, self.amenity):
            key = "{}.{}".format(type(obj).__name__, obj.id)
            self.assertIs(objects[key], obj)

    def test_filter_by_class(self):
        """Class and class-name filters return only matching objects."""
        objects = storage.all(State)
        self.assertIn("State." + self.state.id, objects)
        self.assertTrue(all(isinstance(obj, State)
                            for obj in objects.values()))
        self.assertEqual(storage.all("State"), objects)

    def test_delete(self):
        """Deletion reduces the table's row count after save."""
        before = self.count_rows("reviews")
        storage.delete(self.review)
        storage.save()
        self.assertEqual(self.count_rows("reviews"), before - 1)

    def test_delete_none(self):
        """Deleting None leaves database records intact."""
        before = self.count_rows("states")
        storage.delete()
        storage.save()
        self.assertEqual(self.count_rows("states"), before)

    def test_model_delete(self):
        """The model delete method removes the same database record."""
        self.review.delete()
        storage.save()
        self.assertNotIn("Review." + self.review.id, storage.all())

    def test_update(self):
        """Saved updates survive removal of the ORM session."""
        self.state.name = "New York"
        self.state.save()
        storage.close()
        self.assertEqual(storage.all(State)["State." + self.state.id].name,
                         "New York")

    def test_place_defaults(self):
        """Database inserts apply the required integer defaults."""
        for attribute in ("number_rooms", "number_bathrooms",
                          "max_guest", "price_by_night"):
            self.assertEqual(getattr(self.place, attribute), 0)

    def test_foreign_key_relationships(self):
        """Back references expose each related parent and child."""
        self.assertIn(self.city, self.state.cities)
        self.assertIs(self.city.state, self.state)
        self.assertIn(self.place, self.city.places)
        self.assertIs(self.place.cities, self.city)
        self.assertIn(self.place, self.user.places)
        self.assertIs(self.place.user, self.user)
        self.assertIn(self.review, self.user.reviews)
        self.assertIn(self.review, self.place.reviews)
        self.assertIs(self.review.user, self.user)
        self.assertIs(self.review.place, self.place)

    def test_state_delete_cascades(self):
        """Deleting a state removes its cities, places, and reviews."""
        self.state.delete()
        storage.save()
        for obj in (self.state, self.city, self.place, self.review):
            self.assertNotIn("{}.{}".format(type(obj).__name__, obj.id),
                             storage.all())

    def test_user_delete_cascades(self):
        """Deleting a user removes their places and reviews."""
        self.user.delete()
        storage.save()
        self.assertNotIn("Place." + self.place.id, storage.all())
        self.assertNotIn("Review." + self.review.id, storage.all())
        self.assertIn("City." + self.city.id, storage.all())

    def test_place_delete_cascades(self):
        """Deleting a place removes reviews while preserving its owner."""
        self.place.delete()
        storage.save()
        self.assertNotIn("Review." + self.review.id, storage.all())
        self.assertIn("User." + self.user.id, storage.all())

    def test_many_to_many_amenities(self):
        """Multiple places share amenities through the association table."""
        other = Place(name="Apartment", city_id=self.city.id,
                      user_id=self.user.id)
        other.save()
        self.place.amenities.append(self.amenity)
        other.amenities.append(self.amenity)
        storage.save()
        self.assertEqual(self.count_rows("place_amenity"), 2)
        self.assertIn(self.place, self.amenity.place_amenities)
        self.assertIn(other, self.amenity.place_amenities)
        self.place.delete()
        storage.save()
        self.assertEqual(self.count_rows("place_amenity"), 1)
        self.assertIn("Amenity." + self.amenity.id, storage.all())

    def test_serialization(self):
        """Database model dictionaries contain no ORM instrumentation."""
        data = self.place.to_dict()
        self.assertNotIn("_sa_instance_state", data)
        self.assertEqual(data["__class__"], "Place")
        self.assertEqual(data["city_id"], self.city.id)

    def test_close(self):
        """Close removes the scoped session and permits later queries."""
        session = storage._DBStorage__session
        self.assertTrue(session.registry.has())
        storage.close()
        self.assertFalse(session.registry.has())
        self.assertIn("State." + self.state.id, storage.all())

    def test_reload(self):
        """Reload creates tables and sessions while preserving data."""
        with patch("models.engine.db_storage.Base.metadata") as metadata, \
                patch("models.engine.db_storage.sessionmaker") as factory, \
                patch("models.engine.db_storage.scoped_session") as scoped:
            engine_storage = object.__new__(DBStorage)
            engine_storage._DBStorage__engine = storage._DBStorage__engine
            engine_storage.reload()
        metadata.create_all.assert_called_once_with(
            storage._DBStorage__engine
        )
        metadata.drop_all.assert_not_called()
        factory.assert_called_once_with(bind=storage._DBStorage__engine,
                                        expire_on_commit=False)
        scoped.assert_called_once_with(factory.return_value)
