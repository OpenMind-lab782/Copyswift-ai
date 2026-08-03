import unittest

from payment_engine.services.payment_service import PaymentService
from payment_engine.services.payment_event_service import (
    payment_event_service,
)
from tests.support.factories import PaymentFactory


class CancelPaymentEventTests(unittest.TestCase):

    def setUp(self):
        self.service = PaymentService()
        self.service.clear()
        payment_event_service.clear()

    def test_cancel_records_event(self):

        payment = PaymentFactory.create(
            status="created"
        )

        self.service.save(payment)

        self.service.update_status(
            payment["reference"],
            "cancelled"
        )

        events = payment_event_service.list(
            payment["reference"]
        )

        self.assertEqual(
            events[-1]["event"],
            "cancelled"
        )


if __name__ == "__main__":
    unittest.main()
