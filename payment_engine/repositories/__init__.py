from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)

from payment_engine.repositories.sqlite_payment_event_repository import (
    SQLitePaymentEventRepository,
)

payment_repository = SQLitePaymentRepository()

payment_event_repository = SQLitePaymentEventRepository()
