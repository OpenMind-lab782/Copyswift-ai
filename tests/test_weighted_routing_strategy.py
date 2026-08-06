import unittest

from payment_engine.gateway.metrics import GatewayMetrics
from payment_engine.gateway.weighted_routing import WeightedRoutingStrategy


class WeightedRoutingStrategyTests(unittest.TestCase):

    def setUp(self):
        self.metrics = GatewayMetrics()
        self.strategy = WeightedRoutingStrategy(self.metrics)

    def test_prefers_gateway_with_more_successes(self):

        for _ in range(5):
            self.metrics.record_success("paystack")

        for _ in range(2):
            self.metrics.record_success("flutterwave")

        selected = self.strategy.select(
            ["paystack", "flutterwave"]
        )

        self.assertEqual(
            selected,
            "paystack"
        )

    def test_returns_first_when_scores_are_equal(self):

        selected = self.strategy.select(
            ["stripe", "crypto"]
        )

        self.assertEqual(
            selected,
            "stripe"
        )

    def test_returns_none_for_empty_list(self):

        self.assertIsNone(
            self.strategy.select([])
        )


if __name__ == "__main__":
    unittest.main()
