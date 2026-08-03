import unittest

from payment_engine.services.payment_service import PaymentService
from tests.support.factories import PaymentFactory


class MerchantPaymentCancelTests(unittest.TestCase):

    def setUp(self):
        self.service = PaymentService()
        self.service.clear()

    def test_cancel_payment(self):

        payment = PaymentFactory.create(
            status="created"
        )

        self.service.save(payment)

        cancelled = self.service.update_status(
            payment["reference"],
            "cancelled"
        )

        self.assertEqual(
            cancelled["status"],
            "cancelled"
        )


if __name__ == "__main__":
    unittest.main()
