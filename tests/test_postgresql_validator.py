import os
import unittest

from payment_engine.deployment.postgresql_validator import (
    PostgreSQLDeploymentValidator,
)


class PostgreSQLDeploymentValidatorTests(unittest.TestCase):

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

    def test_missing_database_url_is_not_ready(self):
        self.assertFalse(
            PostgreSQLDeploymentValidator.is_ready()
        )

        report = PostgreSQLDeploymentValidator.report()

        self.assertFalse(report["ready"])
        self.assertIn(
            "DATABASE_URL is not configured",
            report["errors"],
        )

    def test_valid_postgresql_url_is_ready(self):
        os.environ["DATABASE_URL"] = (
            "postgresql+psycopg://"
            "user:password@localhost:5432/swift_payment"
        )

        self.assertTrue(
            PostgreSQLDeploymentValidator.is_ready()
        )

        report = PostgreSQLDeploymentValidator.report()

        self.assertTrue(report["ready"])
        self.assertEqual(
            report["backend"],
            "postgresql",
        )
        self.assertEqual(
            report["driver"],
            "psycopg",
        )

    def test_invalid_database_driver_is_rejected(self):
        os.environ["DATABASE_URL"] = (
            "postgresql://"
            "user:password@localhost:5432/swift_payment"
        )

        self.assertFalse(
            PostgreSQLDeploymentValidator.is_ready()
        )

        report = PostgreSQLDeploymentValidator.report()

        self.assertTrue(
            any(
                "postgresql+psycopg://" in error
                for error in report["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
