import os
import unittest

from sqlalchemy import create_engine, text


class PostgreSQLIntegrationTests(unittest.TestCase):
    """
    Real PostgreSQL integration tests.

    These tests run only when DATABASE_URL is explicitly configured.
    They never require a PostgreSQL server during ordinary local
    Termux development.
    """

    @classmethod
    def setUpClass(cls):
        cls.database_url = os.getenv(
            "DATABASE_URL"
        )

        if not cls.database_url:
            raise unittest.SkipTest(
                "DATABASE_URL is not configured; "
                "real PostgreSQL integration tests skipped."
            )

        if not cls.database_url.startswith(
            "postgresql+psycopg://"
        ):
            raise unittest.SkipTest(
                "DATABASE_URL does not use the "
                "postgresql+psycopg:// driver."
            )

    def test_postgresql_connection(self):
        engine = create_engine(
            self.database_url,
            future=True,
            pool_pre_ping=True,
        )

        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text("SELECT 1")
                )

                self.assertEqual(
                    result.scalar(),
                    1,
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
