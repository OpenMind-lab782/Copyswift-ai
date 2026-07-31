import os
import unittest

from payment_engine.database.postgres_config import PostgreSQLConfig


class PostgreSQLConfigTests(unittest.TestCase):

    def tearDown(self):
        os.environ.pop("DATABASE_URL", None)

    def test_default_url(self):
        url = PostgreSQLConfig.database_url()
        self.assertTrue(url.startswith("postgresql://"))

    def test_configured(self):
        os.environ["DATABASE_URL"] = "postgresql://example"

        self.assertTrue(
            PostgreSQLConfig.is_configured()
        )


if __name__ == "__main__":
    unittest.main()
