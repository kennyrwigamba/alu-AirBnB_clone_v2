#!/usr/bin/python3
"""Display states and their cities from storage."""

import os

from flask import Flask, render_template

from models import storage
from models.state import State


app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)


@app.teardown_appcontext
def close_storage(exception):
    """Close the current storage session after each request."""
    storage.close()


@app.route("/cities_by_states", strict_slashes=False)
def cities_by_states():
    """Render states and their cities sorted by name."""
    states = sorted(
        storage.all(State).values(),
        key=lambda state: state.name,
    )
    return render_template("8-cities_by_states.html", states=states)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
