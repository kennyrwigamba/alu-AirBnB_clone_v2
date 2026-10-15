#!/usr/bin/python3
"""Command interpreter for the AirBnB clone."""

import ast
import cmd
import re
import shlex

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


class HBNBCommand(cmd.Cmd):
    """Interactive command interpreter for model objects."""

    prompt = "(hbnb) "

    classes = {
        "Amenity": Amenity,
        "BaseModel": BaseModel,
        "City": City,
        "Place": Place,
        "Review": Review,
        "State": State,
        "User": User,
    }

    def emptyline(self):
        """Do nothing when the user enters an empty line."""

    def _arguments(self, line):
        """Split a command line while preserving quoted values."""
        try:
            return shlex.split(line)
        except ValueError:
            return []

    def _get_object(self, class_name, object_id):
        """Return an object matching its class and ID, if it exists."""
        key = "{}.{}".format(class_name, object_id)
        return storage.all().get(key)

    def _create_attributes(self, model_class, arguments):
        """Build typed attributes from create command key/value arguments."""
        attributes = {}
        for argument in arguments[1:]:
            if "=" not in argument:
                continue
            key, value = argument.split("=", 1)
            if not key or not value:
                continue
            try:
                if value.startswith('"'):
                    if not value.endswith('"'):
                        continue
                    value = shlex.split(value)[0].replace("_", " ")
                elif "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except (ValueError, IndexError):
                continue
            attributes[key] = value
        return attributes

    def default(self, line):
        """Support Class.command(...) without evaluating executable code."""
        match = re.fullmatch(r"(\w+)\.(\w+)\((.*)\)", line.strip())
        if match is None:
            return super().default(line)
        class_name, command, parameters = match.groups()
        if command not in ("all", "count", "show", "destroy", "update"):
            return super().default(line)
        try:
            arguments = ast.literal_eval("(" + parameters + ",)") \
                if parameters.strip() else ()
        except (ValueError, SyntaxError):
            return super().default(line)
        if command == "update" and len(arguments) == 2 \
                and isinstance(arguments[1], dict):
            for key, value in arguments[1].items():
                self.do_update(" ".join(shlex.quote(str(item)) for item in (
                    class_name, arguments[0], key, value,
                )))
            return
        command_parts = [command, class_name]
        command_parts.extend(shlex.quote(str(value)) for value in arguments)
        return self.onecmd(" ".join(command_parts))

    def do_quit(self, line):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, line):
        """Exit when end-of-file is received."""
        print()
        return True

    def do_create(self, line):
        """Create, persist, and print the ID of a model instance."""
        arguments = re.findall(r'[^\s=]+="(?:\\.|[^"\\])*"|\S+', line)
        if not arguments:
            print("** class name missing **")
            return
        model_class = self.classes.get(arguments[0])
        if model_class is None:
            print("** class doesn't exist **")
            return
        attributes = self._create_attributes(model_class, arguments)
        instance = model_class(**attributes)
        instance.save()
        print(instance.id)

    def do_show(self, line):
        """Print the string representation of a model instance."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        instance = self._get_object(arguments[0], arguments[1])
        if instance is None:
            print("** no instance found **")
            return
        print(instance)

    def do_destroy(self, line):
        """Delete and persist the removal of a model instance."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        if self._get_object(arguments[0], arguments[1]) is None:
            print("** no instance found **")
            return
        storage.delete(self._get_object(arguments[0], arguments[1]))
        storage.save()

    def do_all(self, line):
        """Print string representations of all matching model instances."""
        arguments = self._arguments(line)
        if arguments and arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        class_name = arguments[0] if arguments else None
        objects = storage.all().values()
        if class_name is not None:
            objects = (
                instance for instance in objects
                if instance.__class__.__name__ == class_name
            )
        print([str(instance) for instance in objects])

    def do_count(self, line):
        """Print the number of instances belonging to a model class."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
        elif arguments[0] not in self.classes:
            print("** class doesn't exist **")
        else:
            print(sum(instance.__class__.__name__ == arguments[0]
                      for instance in storage.all().values()))

    def do_update(self, line):
        """Update one simple attribute and persist the model instance."""
        arguments = self._arguments(line)
        if not arguments:
            print("** class name missing **")
            return
        if arguments[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(arguments) < 2:
            print("** instance id missing **")
            return
        instance = self._get_object(arguments[0], arguments[1])
        if instance is None:
            print("** no instance found **")
            return
        if len(arguments) < 3:
            print("** attribute name missing **")
            return
        if len(arguments) < 4:
            print("** value missing **")
            return

        attribute = arguments[2]
        if attribute in ("id", "created_at", "updated_at"):
            return
        value = arguments[3]
        current_value = getattr(instance, attribute, None)
        if isinstance(current_value, bool):
            value = value.lower() == "true"
        else:
            field = getattr(type(instance), attribute, None)
            columns = getattr(getattr(field, "property", None), "columns", [])
            value_type = columns[0].type.python_type if columns \
                else type(current_value)
            if value_type in (int, float):
                try:
                    value = value_type(value)
                except ValueError:
                    return
        setattr(instance, attribute, value)
        instance.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
