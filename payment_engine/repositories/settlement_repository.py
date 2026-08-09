from payment_engine.repositories.sqlite_settlement_repository import (
    SQLiteSettlementRepository,
)


class SettlementRepository(SQLiteSettlementRepository):
    """
    Default settlement repository.

    Kept under the original public class name for backward
    compatibility while delegating persistence to SQLite.
    """

    pass
