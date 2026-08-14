import os
import unittest
from unittest.mock import patch

from payment_engine.factory import RepositoryFactory
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)
from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)


class RepositoryFactoryTests(unittest.TestCase):

    def tearDown(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

    def test_sqlite_default(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.payment_repository()

        self.assertIsInstance(
            repo,
            SQLitePaymentRepository,
        )

    def test_postgres_backend(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLPaymentRepository"
        ) as repository_class:

            repository_class.return_value = (
                object()
            )

            repo = RepositoryFactory.payment_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )


if __name__ == "__main__":
    unittest.main()
