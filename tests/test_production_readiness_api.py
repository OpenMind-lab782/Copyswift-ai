import os
import unittest
from unittest.mock import patch

from app import app


class ProductionReadinessApiTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_ready_uses_development_sqlite_mode(self):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            response = self.client.get("/ready")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["database"], "ok")
        self.assertEqual(body["backend"], "sqlite")
        self.assertEqual(body["version"], "5.0.0")

    def test_ready_returns_503_when_production_postgresql_is_not_ready(self):
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
        ), patch(
            "app.PostgreSQLReadinessService"
        ) as readiness_class:

            readiness_class.return_value.report.return_value = {
                "ready": False,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "errors": [],
                },
                "connection": {
                    "errors": [
                        "PostgreSQL database connection failed"
                    ],
                },
                "schema": {
                    "errors": [],
                },
            }

            response = self.client.get("/ready")

        self.assertEqual(response.status_code, 503)

        body = response.get_json()

        self.assertEqual(body["status"], "not_ready")
        self.assertEqual(body["database"], "unavailable")
        self.assertEqual(body["backend"], "postgresql")
        self.assertEqual(body["driver"], "psycopg")
        self.assertIn(
            "PostgreSQL database connection failed",
            body["errors"],
        )

    def test_ready_returns_200_when_production_postgresql_is_ready(self):
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
        ), patch(
            "app.PostgreSQLReadinessService"
        ) as readiness_class:

            readiness_class.return_value.report.return_value = {
                "ready": True,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "errors": [],
                },
                "connection": {
                    "errors": [],
                },
                "schema": {
                    "errors": [],
                },
            }

            response = self.client.get("/ready")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["database"], "ok")
        self.assertEqual(body["backend"], "postgresql")
        self.assertEqual(body["driver"], "psycopg")

    def test_diagnostics_reports_production_postgresql_state(self):
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
        ), patch(
            "app.PostgreSQLReadinessService"
        ) as readiness_class:

            readiness_class.return_value.report.return_value = {
                "ready": True,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "ready": True,
                    "errors": [],
                },
                "connection": {
                    "ready": True,
                    "connected": True,
                    "errors": [],
                },
                "schema": {
                    "ready": True,
                    "tables": [
                        "payments",
                        "payment_events",
                        "settlements",
                    ],
                    "missing_tables": [],
                    "errors": [],
                },
            }

            response = self.client.get("/diagnostics")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["environment"], "production")
        self.assertEqual(
            body["services"]["database"],
            "ok",
        )
        self.assertIn("postgresql", body)
        self.assertIn("production_validator", body)

    def test_diagnostics_reports_degraded_production_state(self):
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
        ), patch(
            "app.PostgreSQLReadinessService"
        ) as readiness_class:

            readiness_class.return_value.report.return_value = {
                "ready": False,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "ready": True,
                    "errors": [],
                },
                "connection": {
                    "ready": False,
                    "connected": False,
                    "errors": [
                        "PostgreSQL database connection failed"
                    ],
                },
                "schema": {
                    "ready": False,
                    "tables": [],
                    "missing_tables": [],
                    "errors": [],
                },
            }

            response = self.client.get("/diagnostics")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "degraded")
        self.assertEqual(
            body["services"]["database"],
            "not_ready",
        )
        self.assertFalse(
            body["postgresql"]["ready"]
        )


if __name__ == "__main__":
    unittest.main()
