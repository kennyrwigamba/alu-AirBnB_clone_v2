#!/usr/bin/python3
"""Exercise console commands with both supported storage engines."""

from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from uuid import UUID

from console import HBNBCommand
from models import storage
from models.city import City
from models.state import State
from models.user import User
from tests.storage_test_case import StorageTestCase


class TestConsole(StorageTestCase):
    """Check command validation, persistence, and parameter parsing."""

    def setUp(self):
        """Create a console and a saved object in isolated storage."""
        super().setUp()
        self.console = HBNBCommand()
        self.state = State(name="California")
        self.state.save()
        self.user = User(email="console@example.com", password="password")
        self.user.save()
        self.city = City(name="San Francisco", state_id=self.state.id)
        self.city.save()

    def command(self, line):
        """Execute one command and return its printed output."""
        output = StringIO()
        with redirect_stdout(output), patch.object(self.console,
                                                   "stdout", output):
            self.console.onecmd(line)
        return output.getvalue().strip()

    def test_create(self):
        """Create prints a UUID and persists the supplied attributes."""
        object_id = self.command('create State name="New_York"')
        self.assertEqual(UUID(object_id).version, 4)
        self.assertEqual(storage.all()["State." + object_id].name, "New York")

    def test_create_escaped_quotes(self):
        """Escaped double quotes survive string parsing."""
        object_id = self.command(r'create State name="The_\"Bay\"_State"')
        self.assertEqual(
            storage.all()["State." + object_id].name, 'The "Bay" State'
        )

    def test_create_numeric_parameters(self):
        """Integer and float values are inferred from their syntax."""
        object_id = self.command(
            'create Place name="Test" city_id="{}" user_id="{}" '
            'number_rooms=42 latitude=-1.25'.format(
                self.city.id, self.user.id,
            )
        )
        model = storage.all()["Place." + object_id]
        self.assertIs(type(model.number_rooms), int)
        self.assertEqual(model.number_rooms, 42)
        self.assertIs(type(model.latitude), float)
        self.assertEqual(model.latitude, -1.25)

    def test_create_invalid_parameters(self):
        """Unrecognized values are skipped without losing valid ones."""
        object_id = self.command(
            'create Place bad=word broken empty= decimal=1.2.3 '
            'price_by_night=invalid number_rooms=3 name="Nevada" '
            'city_id="{}" user_id="{}"'.format(self.city.id, self.user.id)
        )
        model = storage.all()["Place." + object_id]
        self.assertEqual(model.name, "Nevada")
        self.assertEqual(model.number_rooms, 3)
        self.assertEqual(model.price_by_night, 0)
        for attribute in ("bad", "broken", "empty", "decimal"):
            self.assertNotIn(attribute, model.__dict__)

    def test_create_quoted_numeric_string(self):
        """Quoted numbers remain strings and empty strings are accepted."""
        object_id = self.command('create State name="123"')
        model = storage.all()["State." + object_id]
        self.assertEqual(model.name, "123")
        empty_id = self.command('create State name=""')
        self.assertEqual(storage.all()["State." + empty_id].name, "")

    def test_create_missing_class(self):
        """Create requires a class name."""
        self.assertEqual(self.command("create"), "** class name missing **")

    def test_unknown_classes(self):
        """Every object command rejects unknown class names."""
        for command in ("create", "show", "all", "destroy", "update"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command + " Unknown"),
                    "** class doesn't exist **",
                )

    def test_show(self):
        """Show prints the requested object's representation."""
        self.assertEqual(
            self.command("show State " + self.state.id), str(self.state)
        )

    def test_missing_class(self):
        """Commands requiring a class report when it is missing."""
        for command in ("show", "destroy", "update", "count"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command), "** class name missing **"
                )

    def test_missing_id(self):
        """Object commands require an ID."""
        for command in ("show", "destroy", "update"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command + " State"),
                    "** instance id missing **",
                )

    def test_unknown_id(self):
        """Object commands report IDs that are absent from storage."""
        for command in ("show", "destroy", "update"):
            with self.subTest(command=command):
                self.assertEqual(
                    self.command(command + " State missing"),
                    "** no instance found **",
                )

    def test_all(self):
        """All includes the saved state, with or without a class filter."""
        self.assertIn(self.state.id, self.command("all"))
        self.assertIn(self.state.id, self.command("all State"))
        self.assertEqual(self.command("all Amenity"), "[]")

    def test_destroy(self):
        """Destroy removes and saves the selected instance."""
        self.assertEqual(self.command("destroy State " + self.state.id), "")
        self.assertNotIn("State." + self.state.id, storage.all())

    def test_update(self):
        """Update preserves spaces in quoted string values."""
        self.command('update State {} name "New York"'.format(self.state.id))
        self.assertEqual(self.state.name, "New York")

    def test_update_missing_attribute(self):
        """Update reports a missing attribute name."""
        self.assertEqual(
            self.command("update State " + self.state.id),
            "** attribute name missing **",
        )

    def test_update_missing_value(self):
        """Update reports a missing value."""
        self.assertEqual(
            self.command("update State " + self.state.id + " name"),
            "** value missing **",
        )

    def test_update_protected_fields(self):
        """Updates leave identity and timestamps unchanged."""
        original = self.state.to_dict()
        for attribute in ("id", "created_at", "updated_at"):
            self.command("update State {} {} changed".format(
                self.state.id, attribute,
            ))
        self.assertEqual(self.state.to_dict(), original)

    def test_count(self):
        """Count reports the number of objects belonging to the class."""
        self.assertEqual(
            int(self.command("count State")), len(storage.all(State))
        )

    def test_dotted_commands(self):
        """Dotted all, show, count, and destroy preserve legacy behavior."""
        self.assertIn(self.state.id, self.command("State.all()"))
        self.assertEqual(
            self.command('State.show("{}")'.format(self.state.id)),
            str(self.state),
        )
        self.assertEqual(
            self.command("State.count()"), self.command("count State")
        )
        self.command('State.destroy("{}")'.format(self.state.id))
        self.assertNotIn("State." + self.state.id, storage.all())

    def test_dotted_update(self):
        """Dotted update accepts individual fields and dictionaries."""
        self.command('State.update("{}", "name", "Nevada")'.format(
            self.state.id,
        ))
        self.assertEqual(self.state.name, "Nevada")
        self.command('State.update("{}", {{"name": "New York"}})'.format(
            self.state.id,
        ))
        self.assertEqual(self.state.name, "New York")

    def test_dotted_commands_do_not_execute_code(self):
        """Malformed dotted arguments cannot execute Python functions."""
        with patch("os.system") as system:
            self.command('State.show(__import__("os").system("echo unsafe"))')
        system.assert_not_called()

    def test_empty_line(self):
        """An empty line does not repeat the previous command."""
        self.command("show State " + self.state.id)
        self.assertEqual(self.command(""), "")

    def test_quit_and_eof(self):
        """Quit and EOF stop the command loop."""
        self.assertTrue(self.console.onecmd("quit"))
        with redirect_stdout(StringIO()):
            self.assertTrue(self.console.onecmd("EOF"))

    def test_help(self):
        """Help exposes documentation for object creation."""
        self.assertIn("Create", self.command("help create"))
