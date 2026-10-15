#!/usr/bin/python3
"""Validate the State model and its inherited behavior."""

import unittest

from models.city import City
from models.state import State
from tests.test_models import test_base_model
from tests.storage_test_case import DB_STORAGE


class TestState(test_base_model.TestBaseModel):
    """Check State defaults and common model operations."""

    model_class = State
    defaults = {
        'name': '',
    }

    @unittest.skipIf(DB_STORAGE, "FileStorage relationship getter")
    def test_cities_filter_by_state(self):
        """The cities getter includes only saved cities of this state."""
        state, other = State(), State()
        city = City(state_id=state.id, name="San Francisco")
        unrelated = City(state_id=other.id, name="New York")
        city.save()
        unrelated.save()
        self.assertEqual(state.cities, [city])
        self.assertEqual(other.cities, [unrelated])

    @unittest.skipIf(DB_STORAGE, "FileStorage relationship getter")
    def test_cities_refresh_after_close(self):
        """Reloaded states still resolve the cities saved in JSON storage."""
        from models import storage

        state = State(name="California")
        state.save()
        city = City(state_id=state.id, name="Napa")
        city.save()
        storage.all().clear()
        storage.close()
        restored = storage.all(State)["State." + state.id]
        self.assertEqual([item.id for item in restored.cities], [city.id])

    @unittest.skipIf(DB_STORAGE, "FileStorage relationship getter")
    def test_cities_with_no_matches(self):
        """States without matching saved cities return an empty list."""
        self.assertEqual(State(name="Empty").cities, [])
