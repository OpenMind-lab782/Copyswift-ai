from sqlalchemy import inspect

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.deployment.postgresql_validator import (
    PostgreSQLDeploymentValidator,
)


class PostgreSQLReadinessService:
    """
    Production PostgreSQL readiness and health service.

    Performs configuration validation, database connectivity checks,
    and verification that the core Swift Payment Engine PostgreSQL
    schema is available.
    """

    REQUIRED_TABLES = (
        "payments",
        "payment_events",
        "settlements",
        "reconciliation_records",
        "reconciliation_report_records",
    )

    def __init__(self, database=None):
        self.database = database

    def _configuration_errors(self):
        return PostgreSQLDeploymentValidator.validate_environment()

    def _database(self):
        if self.database is not None:
            return self.database

        return PostgreSQLDatabase()

    def check_connection(self):
        errors = self._configuration_errors()

        if errors:
            return {
                "ready": False,
                "connected": False,
                "errors": errors,
            }

        database = self._database()

        if not database.health_check():
            return {
                "ready": False,
                "connected": False,
                "errors": [
                    "PostgreSQL database connection failed"
                ],
            }

        return {
            "ready": True,
            "connected": True,
            "errors": [],
        }

    def check_schema(self):
        connection_result = self.check_connection()

        if not connection_result["connected"]:
            return {
                "ready": False,
                "tables": [],
                "missing_tables": list(self.REQUIRED_TABLES),
                "errors": connection_result["errors"],
            }

        database = self._database()

        try:
            inspector = inspect(database.engine)
            tables = inspector.get_table_names()

            missing_tables = [
                table
                for table in self.REQUIRED_TABLES
                if table not in tables
            ]

            return {
                "ready": not missing_tables,
                "tables": tables,
                "missing_tables": missing_tables,
                "errors": [],
            }

        except Exception as exc:
            return {
                "ready": False,
                "tables": [],
                "missing_tables": list(self.REQUIRED_TABLES),
                "errors": [
                    f"PostgreSQL schema inspection failed: {exc}"
                ],
            }

    def report(self):
        configuration_errors = self._configuration_errors()

        if configuration_errors:
            return {
                "ready": False,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "ready": False,
                    "errors": configuration_errors,
                },
                "connection": {
                    "ready": False,
                    "connected": False,
                    "errors": configuration_errors,
                },
                "schema": {
                    "ready": False,
                    "tables": [],
                    "missing_tables": list(
                        self.REQUIRED_TABLES
                    ),
                    "errors": configuration_errors,
                },
            }

        connection = self.check_connection()

        if not connection["connected"]:
            return {
                "ready": False,
                "backend": "postgresql",
                "driver": "psycopg",
                "configuration": {
                    "ready": True,
                    "errors": [],
                },
                "connection": connection,
                "schema": {
                    "ready": False,
                    "tables": [],
                    "missing_tables": list(
                        self.REQUIRED_TABLES
                    ),
                    "errors": connection["errors"],
                },
            }

        schema = self.check_schema()

        return {
            "ready": (
                connection["ready"]
                and schema["ready"]
            ),
            "backend": "postgresql",
            "driver": "psycopg",
            "configuration": {
                "ready": True,
                "errors": [],
            },
            "connection": connection,
            "schema": schema,
        }

    def is_ready(self):
        return self.report()["ready"]
