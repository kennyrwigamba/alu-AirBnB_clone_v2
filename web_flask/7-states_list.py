#!/usr/bin/python3
"""Display all states from storage."""

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


@app.route("/states_list", strict_slashes=False)
def states_list():
    """Render all states sorted by name."""
    states = sorted(
        storage.all(State).values(),
        key=lambda state: state.name,
    )
    return render_template("7-states_list.html", states=states)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
