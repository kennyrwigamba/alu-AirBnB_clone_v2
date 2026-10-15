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
