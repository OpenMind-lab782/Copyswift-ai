import unittest

from payment_engine.repositories.settlement_repository import (
    SettlementRepository,
)


class SettlementRepositoryTests(unittest.TestCase):

    def setUp(self):
        self.repository = SettlementRepository()
        self.repository.clear()

    def test_save_and_list(self):

        self.repository.save(
            merchant_id="merchant-001",
            settlement={
                "reference": "PAY-001",
                "amount": 5000,
                "currency": "NGN",
            },
        )

        settlements = self.repository.list(
            "merchant-001"
        )

        self.assertEqual(
            len(settlements),
            1
        )

        self.assertEqual(
            settlements[0]["reference"],
            "PAY-001"
        )


if __name__ == "__main__":
    unittest.main()
