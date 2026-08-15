import os

from payment_engine.database.postgres_config import PostgreSQLConfig


class PostgreSQLDeploymentValidator:
    """
    Validates the minimum PostgreSQL configuration required for
    production deployment of the Swift Payment Engine.
    """

    REQUIRED_ENVIRONMENT = (
        "DATABASE_URL",
        "SWIFT_DB_BACKEND",
    )

    @classmethod
    def validate_environment(cls):
        errors = []

        for variable in cls.REQUIRED_ENVIRONMENT:
            value = os.getenv(variable)

            if not value:
                errors.append(
                    f"{variable} is not configured"
                )

        database_url = os.getenv("DATABASE_URL")

        if database_url and not database_url.startswith(
            "postgresql+psycopg://"
        ):
            errors.append(
                "DATABASE_URL must use the "
                "postgresql+psycopg:// SQLAlchemy driver scheme"
            )

        repository_backend = os.getenv("SWIFT_DB_BACKEND")

        if repository_backend and repository_backend.strip().lower() != "postgres":
            errors.append(
                "SWIFT_DB_BACKEND must be set to 'postgres'"
            )

        return errors

    @classmethod
    def is_ready(cls):
        return not cls.validate_environment()

    @classmethod
    def report(cls):
        errors = cls.validate_environment()

        return {
            "ready": not errors,
            "backend": "postgresql",
            "driver": "psycopg",
            "database_url_configured": PostgreSQLConfig.is_configured(),
            "errors": errors,
        }
