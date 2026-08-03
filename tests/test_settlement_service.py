import unittest

from payment_engine.services.settlement_service import (
    settlement_service,
)


class SettlementServiceTests(unittest.TestCase):

    def setUp(self):
        settlement_service.clear()

    def test_record_settlement(self):

        settlement_service.record(
            merchant_id="merchant-001",
            reference="PAY-001",
            amount=5000,
            currency="NGN",
        )

        settlements = settlement_service.list(
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
