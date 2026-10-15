#!/usr/bin/python3
"""Flask application with a C route."""

from flask import Flask


app = Flask(__name__)


@app.route("/c/<text>", strict_slashes=False)
def c_route(text):
    """Display text prefixed with C."""
    return "C {}".format(text.replace("_", " "))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
