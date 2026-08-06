import unittest

from payment_engine.health_monitor import GatewayHealthMonitor


class TestGatewayHealthMonitor(unittest.TestCase):

    def test_success_rate(self):
        monitor = GatewayHealthMonitor()

        monitor.record_success("paystack")
        monitor.record_success("paystack")
        monitor.record_failure("paystack")

        stats = monitor.snapshot()["paystack"]

        self.assertEqual(stats["total"], 3)
        self.assertAlmostEqual(
            stats["success_rate"],
            2 / 3,
            places=6,
        )

    def test_empty(self):
        monitor = GatewayHealthMonitor()
        self.assertEqual(monitor.snapshot(), {})


if __name__ == "__main__":
    unittest.main()
