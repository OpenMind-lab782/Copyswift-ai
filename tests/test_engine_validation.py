import unittest

from payment_engine.engine import PaymentEngine


class TestEngineValidation(unittest.TestCase):

    def test_validate_engine(self):
        engine = PaymentEngine()

        report = engine.validate_engine()

        self.assertTrue(report["ready"])
        self.assertEqual(
            report["checks"]["engine_status"],
            "healthy"
        )
        self.assertGreater(
            report["checks"]["registered_gateways"],
            0
        )


if __name__ == "__main__":
    unittest.main()
