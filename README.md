# AirBnB clone — The console

This project provides a Python command interpreter for creating and managing
AirBnB objects. It is the first stage of the AirBnB clone application.

The models are BaseModel, User, State, City, Amenity, Place, and Review. Objects
have unique UUIDs and creation/modification timestamps. FileStorage serializes
objects to `file.json` and restores them when the application starts.

## Starting the console

The assignment targets Python 3.8.5 on Ubuntu 20.04. No third-party packages are
required to run the application. From the repository root, run:

```sh
./console.py
# Alternatively:
python3 console.py
```

The prompt is `(hbnb) `. Enter `help` to list commands or `help update` for a
command description. Use `quit` or EOF (Ctrl+D) to exit. Empty lines do nothing.

## Commands

| Command | Usage | Purpose |
| --- | --- | --- |
| create | `create <class>` | Create and save an object; print its ID. |
| show | `show <class> <id>` | Print an object. |
| all | `all [class]` | Print all objects, optionally filtered by class. |
| update | `update <class> <id> <attribute> "<value>"` | Update and save one attribute. |
| destroy | `destroy <class> <id>` | Delete an object and save the removal. |
| help | `help [command]` | Display command help. |
| quit / EOF | `quit` or Ctrl+D | Exit the console. |

Use double quotes for values containing spaces. Existing integer and float
attributes retain their types when updated. Only the first attribute/value pair
is used. Do not update `id`, `created_at`, or `updated_at`; list and datetime
attributes are outside the update command's scope.

## Examples

```text
(hbnb) create User
<generated-id>
(hbnb) update User <generated-id> first_name "Nadiv"
(hbnb) show User <generated-id>
[User] (<generated-id>) {...}
(hbnb) all User
["[User] (<generated-id>) {...}"]
(hbnb) destroy User <generated-id>
(hbnb) quit
```

Replace `<generated-id>` with the ID printed by `create`. Saved objects are
available in subsequent console sessions started from the same directory.
`file.json` is created in the current working directory and is ignored by Git.

The console also accepts piped commands:

```sh
printf 'create State\nall State\nquit\n' | python3 console.py
```

## Tests and style

Run all unit tests from the repository root:

```sh
python3 -m unittest discover tests
# A single test module:
python3 -m unittest tests/test_models/test_base_model.py
# Non-interactive execution:
echo "python3 -m unittest discover tests" | bash
```

Tests mirror the model package and use temporary storage files, preserving
existing application data. They cover all model classes and the storage engine.
The assignment does not require console unit tests.

For the assignment's style check, install and run pycodestyle 2.7.*:

```sh
python3 -m pip install 'pycodestyle==2.7.*'
python3 -m pycodestyle console.py models tests
```

## Layout

- `console.py`: command interpreter.
- `models/`: model definitions and application storage instance.
- `models/engine/`: JSON storage engine.
- `tests/test_models/`: model and storage unit tests.
- `AUTHORS`: repository contributors.