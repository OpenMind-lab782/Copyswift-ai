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
    """
    Central repository backend selector.

    SQLite remains the safe development default.
    PostgreSQL is selected explicitly with:

        SWIFT_DB_BACKEND=postgres

    Unknown backend values fail fast instead of silently falling back
    to SQLite.
    """

    SUPPORTED_BACKENDS = {"sqlite", "postgres"}

    @staticmethod
    def _backend():
        backend = os.getenv(
            "SWIFT_DB_BACKEND",
            "sqlite",
        ).strip().lower()

        if backend not in RepositoryFactory.SUPPORTED_BACKENDS:
            raise ValueError(
                "Unsupported SWIFT_DB_BACKEND: "
                f"{backend!r}. "
                "Expected 'sqlite' or 'postgres'."
            )

        return backend

    @staticmethod
    def backend():
        """Return the normalized active repository backend."""
        return RepositoryFactory._backend()

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
