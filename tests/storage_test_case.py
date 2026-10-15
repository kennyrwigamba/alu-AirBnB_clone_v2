#!/usr/bin/python3
"""Storage fixtures that preserve files and roll back database changes."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from models import storage
from models.engine.file_storage import FileStorage


DB_STORAGE = os.getenv("HBNB_TYPE_STORAGE") == "db"


class StorageTestCase(unittest.TestCase):
    """Give every test an isolated file or database transaction."""

    def setUp(self):
        """Keep all test writes separate from existing application data."""
        if DB_STORAGE:
            from sqlalchemy.orm import scoped_session, sessionmaker

            connection = storage._DBStorage__engine.connect()
            self.addCleanup(connection.close)
            transaction = connection.begin()
            self.addCleanup(transaction.rollback)
            session = scoped_session(sessionmaker(
                bind=connection, expire_on_commit=False,
            ))
            self.addCleanup(session.remove)
            session_patch = patch.object(
                storage, "_DBStorage__session", session
            )
            session_patch.start()
            self.addCleanup(session_patch.stop)
            self.connection = connection
            return

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "file.json"
        for attribute, value in (
            ("_FileStorage__objects", {}),
            ("_FileStorage__file_path", str(self.path)),
        ):
            storage_patch = patch.object(FileStorage, attribute, value)
            storage_patch.start()
            self.addCleanup(storage_patch.stop)
