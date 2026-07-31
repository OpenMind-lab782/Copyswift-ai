import os

from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)


class RepositoryFactory:

    @staticmethod
    def payment_repository():
        backend = os.getenv(
            "SWIFT_DB_BACKEND",
            "sqlite",
        ).lower()

        if backend == "postgres":
            return PostgreSQLPaymentRepository()

        return SQLitePaymentRepository()
