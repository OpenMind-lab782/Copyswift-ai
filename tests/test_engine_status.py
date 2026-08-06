import unittest

from payment_engine.engine import PaymentEngine


class TestEngineStatus(unittest.TestCase):

    def test_engine_status(self):
        engine = PaymentEngine()

        status = engine.get_engine_status()

        self.assertEqual(status["version"], "2.0.0")
        self.assertEqual(status["status"], "healthy")
        self.assertIn("started_at", status)
        self.assertIn("uptime_seconds", status)
        self.assertIn("metrics", status)
        self.assertIn("latency", status)
        self.assertIn("gateway_health", status)


if __name__ == "__main__":
    unittest.main()
