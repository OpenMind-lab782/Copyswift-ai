import os

from tests.base import SwiftEngineTestCase
from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.database.migrations import MigrationManager


class MigrationTests(SwiftEngineTestCase):

    DATABASE = "test_migrations.db"

    def setUp(self):
        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

        self.database = SQLiteDatabase(self.DATABASE)

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.DATABASE):
            os.remove(self.DATABASE)

    def test_schema_version_created(self):
        manager = MigrationManager(self.database)

        manager.initialize()

        self.assertEqual(
            manager.current_version(),
            MigrationManager.CURRENT_VERSION
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
