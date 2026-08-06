import unittest

from payment_engine.engine import PaymentEngine


class TestEndToEnd(unittest.TestCase):

    def test_engine_initializes(self):
        engine = PaymentEngine()
        self.assertIsNotNone(engine)

    def test_verify_duplicate_reference(self):
        engine = PaymentEngine()

        reference = "TEST-REFERENCE-001"

        first = engine.verify_payment("paystack", reference)
        second = engine.verify_payment("paystack", reference)

        self.assertEqual(second.get("status"), "duplicate")


if __name__ == "__main__":
    unittest.main()
