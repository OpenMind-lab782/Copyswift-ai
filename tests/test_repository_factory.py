import os
import unittest

from payment_engine.factory import RepositoryFactory
from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)


class RepositoryFactoryTests(unittest.TestCase):

    def tearDown(self):
        os.environ.pop("SWIFT_DB_BACKEND", None)

    def test_sqlite_default(self):
        repo = RepositoryFactory.payment_repository()

        self.assertIsInstance(
            repo,
            SQLitePaymentRepository,
        )

    def test_postgres_backend(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        repo = RepositoryFactory.payment_repository()

        self.assertIsInstance(
            repo,
            PostgreSQLPaymentRepository,
        )


if __name__ == "__main__":
    unittest.main()
