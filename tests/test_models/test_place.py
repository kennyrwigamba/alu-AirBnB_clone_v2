#!/usr/bin/python3
"""Validate the Place model and its inherited behavior."""

import unittest

from models.amenity import Amenity
from models.place import Place
from models.review import Review
from tests.test_models import test_base_model
from tests.storage_test_case import DB_STORAGE


class TestPlace(test_base_model.TestBaseModel):
    """Check Place defaults and common model operations."""

    model_class = Place
    defaults = {
        'city_id': '',
        'user_id': '',
        'name': '',
        'description': '',
        'number_rooms': 0,
        'number_bathrooms': 0,
        'max_guest': 0,
        'price_by_night': 0,
        'latitude': 0.0,
        'longitude': 0.0,
        'amenity_ids': [],
    }

    def test_amenity_lists_are_independent(self):
        """Changing one place's amenities does not affect another place."""
        first, second = Place(), Place()
        first.amenity_ids.append("amenity-id")
        self.assertEqual(second.amenity_ids, [])
        self.assertEqual(Place.amenity_ids, [])

    @unittest.skipIf(DB_STORAGE, "FileStorage relationship getter")
    def test_reviews_filter_by_place(self):
        """The reviews getter excludes reviews for other places."""
        place, other = Place(), Place()
        review = Review(place_id=place.id, text="Great")
        unrelated = Review(place_id=other.id, text="Other place")
        review.save()
        unrelated.save()
        self.assertEqual(place.reviews, [review])

    @unittest.skipIf(DB_STORAGE, "FileStorage relationship setter")
    def test_amenities_getter_and_setter(self):
        """Amenities accept saved Amenity objects and ignore other types."""
        place = Place()
        wifi, oven = Amenity(name="Wifi"), Amenity(name="Oven")
        wifi.save()
        oven.save()
        place.amenities = wifi
        place.amenities = wifi
        place.amenities = "invalid"
        self.assertEqual(place.amenity_ids, [wifi.id])
        self.assertEqual(place.amenities, [wifi])
        place.amenities = oven
        self.assertCountEqual(place.amenities, [wifi, oven])
