from payment_engine.repositories.sqlite_reconciliation_repository import (
    SQLiteReconciliationRepository,
)


class ReconciliationRepository(SQLiteReconciliationRepository):
    """
    Default reconciliation repository.

    Kept under the original public class name for backward
    compatibility while delegating persistence to SQLite.
    """

    pass
