import unittest
from unittest.mock import MagicMock

from payment_engine.database.postgres_schema import (
    initialize_postgres_schema,
)
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)


class PostgreSQLSchemaDecouplingTests(unittest.TestCase):

    def test_payment_repository_construction_does_not_initialize_schema(self):
        database = MagicMock()

        PostgreSQLPaymentRepository(database=database)

        database.engine.begin.assert_not_called()

    def test_payment_repository_construction_keeps_database_reference(self):
        database = MagicMock()

        repository = PostgreSQLPaymentRepository(database=database)

        self.assertIs(repository.db, database)

    def test_explicit_schema_initializer_is_available(self):
        database = MagicMock()

        initialize_postgres_schema(database)

        database.engine.begin.assert_called_once()

    def test_schema_initializer_is_not_imported_as_repository_dependency(self):
        import payment_engine.repositories.postgres_payment_repository as module

        self.assertFalse(
            hasattr(module, "initialize_postgres_schema")
        )


if __name__ == "__main__":
    unittest.main()
