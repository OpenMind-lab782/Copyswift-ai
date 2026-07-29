import unittest

from payment_engine.metrics import MetricsCollector


class TestMetricsCollector(unittest.TestCase):

    def test_increment(self):
        m = MetricsCollector()
        m.increment("payments")
        self.assertEqual(m.get("payments"), 1)

    def test_increment_multiple(self):
        m = MetricsCollector()
        m.increment("payments", 5)
        self.assertEqual(m.get("payments"), 5)

    def test_snapshot(self):
        m = MetricsCollector()
        m.increment("success")
        snap = m.snapshot()
        self.assertEqual(snap["success"], 1)

    def test_reset(self):
        m = MetricsCollector()
        m.increment("payments")
        m.reset()
        self.assertEqual(m.get("payments"), 0)


if __name__ == "__main__":
    unittest.main()
