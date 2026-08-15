import os

from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)
from payment_engine.repositories.sqlite_payment_event_repository import (
    SQLitePaymentEventRepository,
)
from payment_engine.repositories.postgres_payment_event_repository import (
    PostgreSQLPaymentEventRepository,
)


class RepositoryFactory:

    @staticmethod
    def _backend():
        return os.getenv(
            "SWIFT_DB_BACKEND",
            "sqlite",
        ).lower()

    @staticmethod
    def payment_repository():
        if RepositoryFactory._backend() == "postgres":
            return PostgreSQLPaymentRepository()

        return SQLitePaymentRepository()

    @staticmethod
    def payment_event_repository():
        if RepositoryFactory._backend() == "postgres":
            return PostgreSQLPaymentEventRepository()

        return SQLitePaymentEventRepository()
