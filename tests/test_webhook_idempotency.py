import unittest

from payment_engine.webhooks import WebhookIdempotencyManager


class WebhookIdempotencyTests(unittest.TestCase):

    def test_first_event_is_processed(self):
        manager = WebhookIdempotencyManager()

        self.assertTrue(
            manager.process("evt-001")
        )

    def test_duplicate_event_is_rejected(self):
        manager = WebhookIdempotencyManager()

        manager.process("evt-001")

        self.assertFalse(
            manager.process("evt-001")
        )

    def test_different_events(self):
        manager = WebhookIdempotencyManager()

        self.assertTrue(manager.process("evt-001"))
        self.assertTrue(manager.process("evt-002"))


if __name__ == "__main__":
    unittest.main()
