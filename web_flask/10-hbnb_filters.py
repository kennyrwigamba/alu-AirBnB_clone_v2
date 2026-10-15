#!/usr/bin/python3
"""Display the HBNB filters page."""

import os

from flask import Flask, render_template

from models import storage
from models.amenity import Amenity
from models.city import City
from models.state import State


app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)


@app.teardown_appcontext
def close_storage(exception):
    """Close the current storage session after each request."""
    storage.close()


@app.route("/hbnb_filters", strict_slashes=False)
def hbnb_filters():
    """Render sorted states, cities, and amenities."""
    states = sorted(
        storage.all(State).values(),
        key=lambda state: state.name,
    )
    cities = sorted(
        storage.all(City).values(),
        key=lambda city: city.name,
    )
    amenities = sorted(
        storage.all(Amenity).values(),
        key=lambda amenity: amenity.name,
    )
    return render_template(
        "10-hbnb_filters.html",
        states=states,
        cities=cities,
        amenities=amenities,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
