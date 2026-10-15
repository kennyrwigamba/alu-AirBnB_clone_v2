# AirBnB clone — The console

This project provides a Python command interpreter for creating and managing
AirBnB objects. It is the first stage of the AirBnB clone application.

The models are BaseModel, User, State, City, Amenity, Place, and Review. Objects
have unique UUIDs and creation/modification timestamps. FileStorage serializes
objects to `file.json` and restores them when the application starts.

## Starting the console

The assignment targets Python 3.8.5 on Ubuntu 20.04. FileStorage requires only
the Python standard library. MySQL storage requires SQLAlchemy 1.4 and
mysqlclient. From the repository root, run:

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
| create | `create <class> [key=value ...]` | Create and save an object; print its ID. |
| show | `show <class> <id>` | Print an object. |
| all | `all [class]` | Print all objects, optionally filtered by class. |
| update | `update <class> <id> <attribute> "<value>"` | Update and save one attribute. |
| destroy | `destroy <class> <id>` | Delete an object and save the removal. |
| count | `count <class>` | Print the number of objects of a class. |
| help | `help [command]` | Display command help. |
| quit / EOF | `quit` or Ctrl+D | Exit the console. |

Use double quotes for values containing spaces. Existing integer and float
attributes retain their types when updated. Only the first attribute/value pair
is used. Do not update `id`, `created_at`, or `updated_at`; list and datetime
attributes are outside the update command's scope.

For `create`, quote strings and use underscores for spaces, for example
`create State name="New_York"`. Unquoted integers and decimal numbers are
converted to their numeric types; invalid parameters are skipped. Dotted
commands such as `State.all()`, `State.count()`, and
`State.update("<id>", {"name": "New York"})` are also supported.

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

To test MySQL storage, prepare the dedicated test database and install its
dependencies first:

```sh
python3 -m pip install 'SQLAlchemy==1.4.54' 'mysqlclient==2.2.7'
mysql -uroot -p < setup_mysql_test.sql
HBNB_ENV=test HBNB_TYPE_STORAGE=db \
HBNB_MYSQL_USER=hbnb_test HBNB_MYSQL_PWD=hbnb_test_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_test_db \
python3 -m unittest discover tests
```

`HBNB_ENV=test` clears the selected database's tables when storage is created;
use the dedicated test database. Tests cover the console, every model, and both
storage engines. File tests use temporary files; database tests roll back their
transactions after each test. Engine-specific tests use unittest skip decorators
when the other storage engine is selected. New objects enter storage on `save()`.

For the assignment's style check, install and run pycodestyle 2.7.*:

```sh
python3 -m pip install 'pycodestyle==2.7.*'
python3 -m pycodestyle console.py models tests
```

## Layout

- `console.py`: command interpreter.
- `models/`: model definitions and application storage instance.
- `models/engine/`: JSON and MySQL storage engines.
- `tests/test_console.py`: command validation and console persistence tests.
- `tests/test_models/`: model and storage unit tests.
- `AUTHORS`: repository contributors.
