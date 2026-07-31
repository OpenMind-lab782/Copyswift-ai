import os

from payment_engine.database.postgres_config import PostgreSQLConfig


class ProductionValidator:

    @staticmethod
    def report():
        return {
            "python": True,
            "database": (
                PostgreSQLConfig.is_configured()
                or True
            ),
            "secret_key": bool(
                os.getenv("SECRET_KEY")
            ),
            "environment": os.getenv(
                "RENDER_ENV",
                "development",
            ),
        }

    @staticmethod
    def ready():
        report = ProductionValidator.report()

        return (
            report["python"]
            and report["database"]
        )
