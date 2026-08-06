import unittest

from payment_engine.repositories.reconciliation_repository import (
    ReconciliationRepository,
)


class ReconciliationRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.repository = ReconciliationRepository()
        self.repository.clear()

    def test_save_and_list_records(self):

        self.repository.save(
            merchant_id="merchant-001",
            record={
                "reference": "PAY-001",
            },
        )

        records = self.repository.list(
            "merchant-001"
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["reference"],
            "PAY-001"
        )


if __name__ == "__main__":
    unittest.main()
