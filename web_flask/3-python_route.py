#!/usr/bin/python3
"""Flask application with a Python route."""

from flask import Flask


app = Flask(__name__)


@app.route("/python", defaults={"text": "is cool"}, strict_slashes=False)
@app.route("/python/<text>", strict_slashes=False)
def python_route(text):
    """Display text prefixed with Python."""
    return "Python {}".format(text.replace("_", " "))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
