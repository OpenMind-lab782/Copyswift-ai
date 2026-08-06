import unittest

from payment_engine.gateway.health import GatewayHealthMonitor


class GatewayHealthMonitorTests(unittest.TestCase):

    def setUp(self):
        self.monitor = GatewayHealthMonitor()

    def test_mark_gateway_healthy(self):

        self.monitor.set_status(
            "paystack",
            "healthy"
        )

        self.assertEqual(
            self.monitor.get_status("paystack"),
            "healthy"
        )

    def test_unknown_gateway_defaults_to_unknown(self):

        self.assertEqual(
            self.monitor.get_status("stripe"),
            "unknown"
        )

    def test_list_statuses(self):

        self.monitor.set_status(
            "paystack",
            "healthy"
        )

        self.monitor.set_status(
            "flutterwave",
            "degraded"
        )

        statuses = self.monitor.list()

        self.assertEqual(
            statuses["paystack"],
            "healthy"
        )

        self.assertEqual(
            statuses["flutterwave"],
            "degraded"
        )


if __name__ == "__main__":
    unittest.main()
