import os
import unittest

from payment_engine.database.postgres_config import PostgreSQLConfig


class PostgreSQLConfigTests(unittest.TestCase):

    def setUp(self):
        self.original_database_url = os.environ.get(
            "DATABASE_URL"
        )

    def tearDown(self):
        if self.original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = (
                self.original_database_url
            )

    def test_default_url(self):
        os.environ.pop("DATABASE_URL", None)

        url = PostgreSQLConfig.database_url()

        self.assertTrue(
            url.startswith("postgresql+psycopg://")
        )

        self.assertIn(
            "swift_payment",
            url,
        )

    def test_configured(self):
        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "test:test@localhost:5432/swift_payment"
        )

        self.assertTrue(
            PostgreSQLConfig.is_configured()
        )

        self.assertEqual(
            PostgreSQLConfig.database_url(),
            os.environ["DATABASE_URL"],
        )


if __name__ == "__main__":
    unittest.main()
