import os
import tempfile
import unittest

from payment_engine.database.sqlite import SQLiteDatabase
from payment_engine.repositories.sqlite_payment_event_repository import (
    SQLitePaymentEventRepository,
)
from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)
from payment_engine.services.payment_service import PaymentService
from payment_engine.services.payment_event_service import PaymentEventService


class FailingEventRepository(SQLitePaymentEventRepository):

    def save(self, reference, event, connection=None):
        raise RuntimeError("event persistence failed")


class FailingEventService(PaymentEventService):

    def __init__(self, repository):
        super().__init__(repository=repository)


class PaymentAtomicityTests(unittest.TestCase):

    def setUp(self):
        fd, self.database_path = tempfile.mkstemp(
            prefix="batch74_payment_atomicity_",
            suffix=".db",
        )
        os.close(fd)

        self.database = SQLiteDatabase(self.database_path)
        self.payment_repository = SQLitePaymentRepository(
            self.database
        )
        self.event_repository = FailingEventRepository(
            self.database
        )

        self.event_service = FailingEventService(
            self.event_repository
        )

        self.service = PaymentService(
            payment_repository=self.payment_repository,
            payment_event_service=self.event_service,
        )

    def tearDown(self):
        self.database.close()

        if os.path.exists(self.database_path):
            os.remove(self.database_path)

    def test_payment_and_created_event_must_be_atomic(self):

        payment = {
            "reference": "ATOMIC-001",
            "merchant_id": "merchant-001",
            "amount": 1000,
            "currency": "NGN",
            "status": "pending",
            "gateway": "paystack",
            "customer_email": "customer@example.com",
            "metadata": {},
            "idempotency_key": None,
        }

        with self.assertRaises(RuntimeError):
            self.service.save(payment)

        self.assertEqual(
            self.payment_repository.list(),
            [],
            "Payment must not remain persisted when event recording fails",
        )



    def test_verification_state_change_rolls_back_when_event_persistence_fails(self):
        payment = {
            "reference": "ATOMIC-VERIFY-001",
            "merchant_id": "merchant-076",
            "amount": 1000,
            "currency": "NGN",
            "status": "pending",
            "gateway": "paystack",
            "customer_email": "customer@example.com",
            "metadata": {},
            "idempotency_key": None,
        }

        self.payment_repository.save(payment)

        with self.assertRaises(RuntimeError):
            self.service.update_status(
                "ATOMIC-VERIFY-001",
                "verified",
            )

        stored = self.payment_repository.get(
            "ATOMIC-VERIFY-001"
        )

        self.assertEqual(
            stored.get("status"),
            "pending",
            "Payment status must roll back when verification event persistence fails",
        )

        self.assertEqual(
            self.event_repository.list(
                "ATOMIC-VERIFY-001"
            ),
            [],
            "Verification event must not remain persisted after rollback",
        )


if __name__ == "__main__":
    unittest.main()
