#!/usr/bin/python3
"""Display states, optionally filtered by ID."""

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


@app.route("/states", strict_slashes=False)
def states():
    """Render all states sorted by name."""
    states = sorted(
        storage.all(State).values(),
        key=lambda state: state.name,
    )
    return render_template("9-states.html", states=states)


@app.route("/states/<state_id>", strict_slashes=False)
def state_by_id(state_id):
    """Render a state and its cities selected by ID."""
    state = storage.all(State).get("State.{}".format(state_id))
    return render_template("9-states.html", state=state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
