import unittest

from payment_engine.config import EngineConfig


class TestEngineConfig(unittest.TestCase):

    def test_default_values(self):
        cfg = EngineConfig()

        self.assertEqual(cfg.retry_attempts, 3)
        self.assertEqual(cfg.timeout_seconds, 5.0)
        self.assertTrue(cfg.enable_events)
        self.assertTrue(cfg.enable_metrics)

    def test_custom_values(self):
        cfg = EngineConfig(
            retry_attempts=5,
            timeout_seconds=10.0,
        )

        self.assertEqual(cfg.retry_attempts, 5)
        self.assertEqual(cfg.timeout_seconds, 10.0)


if __name__ == "__main__":
    unittest.main()
