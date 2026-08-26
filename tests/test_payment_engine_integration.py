import unittest

from payment_engine.engine import PaymentEngine
from payment_engine.services.payment_service import PaymentService


class TestPaymentEngineIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = PaymentEngine()
        self.payment_service = PaymentService()
        self.payment_service.clear()
        self.engine.payment_event_service.clear()

    def _create_payment(self, reference, gateway="paystack"):
        self.payment_service.save({
            "reference": reference,
            "merchant_id": "merchant-076",
            "amount": 100,
            "currency": "NGN",
            "status": "pending",
            "gateway": gateway,
            "customer_email": "customer@example.com",
            "metadata": {},
            "idempotency_key": None,
        })

    def test_verify_payment_success(self):
        reference = "INTEGRATION-REF-001"

        self._create_payment(reference)

        result = self.engine.verify_payment(
            "paystack",
            reference
        )

        self.assertEqual(
            result.get("status"),
            "verified"
        )

        stored = self.payment_service.get(reference)

        self.assertEqual(
            stored.get("status"),
            "verified"
        )

    def test_duplicate_reference(self):
        reference = "INTEGRATION-DUP-001"

        self._create_payment(reference)

        self.engine.verify_payment(
            "paystack",
            reference
        )

        second = self.engine.verify_payment(
            "paystack",
            reference
        )

        self.assertEqual(
            second.get("status"),
            "duplicate"
        )

    def test_verified_reference_is_persistent_across_engine_instances(self):
        reference = "INTEGRATION-PERSISTENT-VERIFY-001"

        self._create_payment(reference)

        first_engine = self.engine

        first = first_engine.verify_payment(
            "paystack",
            reference,
        )

        self.assertEqual(
            first.get("status"),
            "verified",
        )

        second_engine = PaymentEngine()

        second = second_engine.verify_payment(
            "paystack",
            reference,
        )

        self.assertEqual(
            second.get("status"),
            "duplicate",
        )

        stored = self.payment_service.get(reference)

        self.assertEqual(
            stored.get("status"),
            "verified",
        )

    def test_multiple_providers(self):
        payments = {
            "paystack": "INTEGRATION-PAYSTACK-001",
            "flutterwave": "INTEGRATION-FLUTTERWAVE-001",
        }

        for provider, reference in payments.items():
            self._create_payment(
                reference,
                gateway=provider,
            )

            result = self.engine.verify_payment(
                provider,
                reference
            )

            self.assertEqual(
                result.get("status"),
                "verified"
            )

            stored = self.payment_service.get(reference)

            self.assertEqual(
                stored.get("status"),
                "verified"
            )


if __name__ == "__main__":
    unittest.main()
