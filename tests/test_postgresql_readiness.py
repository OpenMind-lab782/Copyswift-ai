import os
import unittest

from sqlalchemy import create_engine, text

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.deployment.postgresql_readiness import (
    PostgreSQLReadinessService,
)


class PostgreSQLReadinessServiceTests(unittest.TestCase):

    REQUIRED_TABLES = (
        "payments",
        "payment_events",
        "settlements",
        "reconciliation_records",
        "reconciliation_report_records",
    )

    def setUp(self):
        self.original_database_url = os.environ.get(
            "DATABASE_URL"
        )

        os.environ.pop("DATABASE_URL", None)

    def tearDown(self):
        if self.original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = (
                self.original_database_url
            )

    def _configured_sqlite_database(self):
        engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=engine,
        )

        return database

    def _create_required_tables(self, database):
        with database.engine.begin() as connection:
            for table in self.REQUIRED_TABLES:
                connection.execute(
                    text(
                        f"""
                        CREATE TABLE {table} (
                            id INTEGER PRIMARY KEY
                        )
                        """
                    )
                )

    def test_missing_configuration_is_not_ready(self):
        service = PostgreSQLReadinessService()

        self.assertFalse(
            service.is_ready()
        )

        report = service.report()

        self.assertFalse(report["ready"])
        self.assertFalse(
            report["configuration"]["ready"]
        )
        self.assertIn(
            "DATABASE_URL is not configured",
            report["configuration"]["errors"],
        )

    def test_connection_failure_is_not_ready(self):
        class UnhealthyDatabase:
            def health_check(self):
                return False

        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "user:password@localhost:5432/swift_payment"
        )

        service = PostgreSQLReadinessService(
            database=UnhealthyDatabase()
        )

        result = service.check_connection()

        self.assertFalse(result["ready"])
        self.assertFalse(result["connected"])
        self.assertIn(
            "PostgreSQL database connection failed",
            result["errors"],
        )

    def test_missing_schema_tables_are_reported(self):
        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "user:password@localhost:5432/swift_payment"
        )

        database = self._configured_sqlite_database()

        service = PostgreSQLReadinessService(
            database=database
        )

        result = service.check_schema()

        self.assertFalse(result["ready"])
        self.assertEqual(
            set(result["missing_tables"]),
            set(self.REQUIRED_TABLES),
        )

    def test_complete_schema_is_ready(self):
        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "user:password@localhost:5432/swift_payment"
        )

        database = self._configured_sqlite_database()

        self._create_required_tables(database)

        service = PostgreSQLReadinessService(
            database=database
        )

        result = service.check_schema()

        self.assertTrue(result["ready"])
        self.assertEqual(
            result["missing_tables"],
            [],
        )

        for table in self.REQUIRED_TABLES:
            self.assertIn(
                table,
                result["tables"],
            )

    def test_complete_environment_and_schema_are_ready(self):
        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "user:password@localhost:5432/swift_payment"
        )

        database = self._configured_sqlite_database()

        self._create_required_tables(database)

        service = PostgreSQLReadinessService(
            database=database
        )

        report = service.report()

        self.assertTrue(report["ready"])
        self.assertEqual(
            report["backend"],
            "postgresql",
        )
        self.assertEqual(
            report["driver"],
            "psycopg",
        )
        self.assertTrue(
            report["configuration"]["ready"]
        )
        self.assertTrue(
            report["connection"]["ready"]
        )
        self.assertTrue(
            report["connection"]["connected"]
        )
        self.assertTrue(
            report["schema"]["ready"]
        )
        self.assertEqual(
            report["schema"]["missing_tables"],
            [],
        )

    def test_invalid_database_configuration_prevents_connection(self):
        os.environ["DATABASE_URL"] = (
            "postgresql://"
            "user:password@localhost:5432/swift_payment"
        )

        service = PostgreSQLReadinessService()

        result = service.check_connection()

        self.assertFalse(result["ready"])
        self.assertFalse(result["connected"])
        self.assertTrue(
            any(
                "postgresql+psycopg://" in error
                for error in result["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
