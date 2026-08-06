import unittest

from payment_engine.gateway.metrics import GatewayMetrics


class GatewayMetricsTests(unittest.TestCase):

    def setUp(self):
        self.metrics = GatewayMetrics()

    def test_records_success(self):
        self.metrics.record_success("paystack")

        stats = self.metrics.get("paystack")

        self.assertEqual(stats["success"], 1)
        self.assertEqual(stats["failure"], 0)

    def test_records_failure(self):
        self.metrics.record_failure("stripe")

        stats = self.metrics.get("stripe")

        self.assertEqual(stats["success"], 0)
        self.assertEqual(stats["failure"], 1)

    def test_unknown_gateway_defaults_to_zero(self):
        stats = self.metrics.get("crypto")

        self.assertEqual(
            stats,
            {
                "success": 0,
                "failure": 0
            }
        )


if __name__ == "__main__":
    unittest.main()
