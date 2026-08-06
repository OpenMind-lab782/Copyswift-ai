import unittest

from payment_engine.services.reconciliation_service import (
    reconciliation_service,
)


class ReconciliationServiceTests(unittest.TestCase):

    def setUp(self):
        reconciliation_service.clear()

    def test_mark_payment_as_reconciled(self):

        reconciliation_service.record(
            merchant_id="merchant-001",
            reference="PAY-001",
        )

        reconciled = reconciliation_service.list(
            "merchant-001"
        )

        self.assertEqual(len(reconciled), 1)
        self.assertEqual(
            reconciled[0]["reference"],
            "PAY-001"
        )


if __name__ == "__main__":
    unittest.main()
