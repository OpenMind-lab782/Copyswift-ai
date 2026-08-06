import unittest

from payment_engine.middleware.idempotency import (
    IdempotencyStore,
)


class IdempotencyStoreTests(unittest.TestCase):

    def setUp(self):
        self.store = IdempotencyStore()

    def test_first_request_is_new(self):
        self.assertTrue(
            self.store.register("payment-001")
        )

    def test_duplicate_request_is_rejected(self):
        self.store.register("payment-001")

        self.assertFalse(
            self.store.register("payment-001")
        )

    def test_clear_store(self):
        self.store.register("payment-001")

        self.store.clear()

        self.assertTrue(
            self.store.register("payment-001")
        )


if __name__ == "__main__":
    unittest.main()
