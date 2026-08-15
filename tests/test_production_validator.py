import os
import unittest
from unittest.mock import patch

from payment_engine.deployment import ProductionValidator


class ProductionValidatorTests(unittest.TestCase):

    def test_report_exists(self):
        report = ProductionValidator.report()

        self.assertIn("python", report)
        self.assertIn("database", report)
        self.assertIn("secret_key", report)
        self.assertIn("environment", report)
        self.assertIn("postgresql_configured", report)
        self.assertIn("repository_backend", report)
        self.assertIn("production_environment", report)
        self.assertIn("postgresql_errors", report)

    def test_development_does_not_require_production_configuration(self):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            report = ProductionValidator.report()

        self.assertEqual(
            report["environment"],
            "development",
        )
        self.assertFalse(
            report["production_environment"]
        )
        self.assertTrue(report["database"])
        self.assertTrue(report["secret_key"])
        self.assertTrue(
            ProductionValidator.ready()
        )

    def test_production_requires_database_url(self):
        with patch.dict(
            os.environ,
            {
                "RENDER_ENV": "production",
                "SECRET_KEY": "test-secret",
            },
            clear=True,
        ):
            report = ProductionValidator.report()

        self.assertTrue(
            report["production_environment"]
        )
        self.assertFalse(report["database"])
        self.assertIn(
            "DATABASE_URL is not configured",
            report["postgresql_errors"],
        )

    def test_production_requires_secret_key(self):
        with patch.dict(
            os.environ,
            {
                "RENDER_ENV": "production",
                "SWIFT_DB_BACKEND": "postgres",
                "DATABASE_URL": (
                    "postgresql+psycopg://"
                    "user:password@localhost:5432/swift_payment"
                ),
            },
            clear=True,
        ):
            report = ProductionValidator.report()

        self.assertTrue(report["database"])
        self.assertFalse(report["secret_key"])

    def test_production_rejects_invalid_database_url_scheme(self):
        with patch.dict(
            os.environ,
            {
                "RENDER_ENV": "production",
                "SWIFT_DB_BACKEND": "postgres",
                "DATABASE_URL": (
                    "postgresql://"
                    "user:password@localhost:5432/swift_payment"
                ),
                "SECRET_KEY": "test-secret",
            },
            clear=True,
        ):
            report = ProductionValidator.report()

        self.assertFalse(report["database"])
        self.assertTrue(
            any(
                "postgresql+psycopg://" in error
                for error in report["postgresql_errors"]
            )
        )

    def test_production_is_ready_with_valid_configuration(self):
        with patch.dict(
            os.environ,
            {
                "RENDER_ENV": "production",
                "SWIFT_DB_BACKEND": "postgres",
                "DATABASE_URL": (
                    "postgresql+psycopg://"
                    "user:password@localhost:5432/swift_payment"
                ),
                "SECRET_KEY": "test-secret",
            },
            clear=True,
        ):
            report = ProductionValidator.report()

            self.assertTrue(
                report["production_environment"]
            )
            self.assertTrue(report["database"])
            self.assertTrue(report["secret_key"])
            self.assertTrue(
                ProductionValidator.ready()
            )


if __name__ == "__main__":
    unittest.main()
