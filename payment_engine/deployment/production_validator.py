import os

from payment_engine.database.postgres_config import PostgreSQLConfig
from payment_engine.deployment.postgresql_validator import (
    PostgreSQLDeploymentValidator,
)


class ProductionValidator:
    """
    Validates the minimum production configuration required by the
    Swift Payment Engine.

    Development remains supported without PostgreSQL or SECRET_KEY.

    Production readiness requires:
    - PostgreSQL DATABASE_URL configuration
    - the postgresql+psycopg:// SQLAlchemy driver scheme
    - SECRET_KEY configuration
    - SWIFT_DB_BACKEND=postgres
    """

    @staticmethod
    def report():
        environment = os.getenv(
            "RENDER_ENV",
            "development",
        ).strip().lower()

        production_environment = environment in {
            "production",
            "prod",
        }

        postgres_configured = PostgreSQLConfig.is_configured()

        repository_backend = os.getenv(
            "SWIFT_DB_BACKEND"
        )

        postgres_errors = (
            PostgreSQLDeploymentValidator.validate_environment()
            if production_environment
            else []
        )

        database_ready = (
            not postgres_errors
            if production_environment
            else True
        )

        secret_key_configured = bool(
            os.getenv("SECRET_KEY")
        )

        secret_key_ready = (
            secret_key_configured
            if production_environment
            else True
        )

        return {
            "python": True,
            "database": database_ready,
            "secret_key": secret_key_ready,
            "environment": environment,
            "postgresql_configured": postgres_configured,
            "repository_backend": repository_backend,
            "production_environment": production_environment,
            "postgresql_errors": postgres_errors,
        }

    @staticmethod
    def ready():
        report = ProductionValidator.report()

        return (
            report["python"]
            and report["database"]
            and report["secret_key"]
        )
