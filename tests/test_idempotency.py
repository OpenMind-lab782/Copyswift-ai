import unittest

from payment_engine.idempotency import IdempotencyManager


class IdempotencyManagerTests(unittest.TestCase):

    def test_mark_and_check_processed(self):
        manager = IdempotencyManager()

        manager.mark_processed("PAY-001")

        self.assertTrue(
            manager.is_processed("PAY-001")
        )

    def test_forget_removes_single_reference(self):
        manager = IdempotencyManager()

        manager.mark_processed("PAY-001")
        manager.mark_processed("PAY-002")

        manager.forget("PAY-001")

        self.assertFalse(
            manager.is_processed("PAY-001")
        )
        self.assertTrue(
            manager.is_processed("PAY-002")
        )

    def test_forget_missing_reference_is_safe(self):
        manager = IdempotencyManager()

        manager.forget("UNKNOWN")

        self.assertFalse(
            manager.is_processed("UNKNOWN")
        )

    def test_reset_clears_all_references(self):
        manager = IdempotencyManager()

        manager.mark_processed("PAY-001")
        manager.mark_processed("PAY-002")

        manager.reset()

        self.assertFalse(
            manager.is_processed("PAY-001")
        )
        self.assertFalse(
            manager.is_processed("PAY-002")
        )


if __name__ == "__main__":
    unittest.main()
