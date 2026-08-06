import unittest

from payment_engine.services.reconciliation_report_service import (
    reconciliation_report_service,
)


class ReconciliationReportServiceTests(unittest.TestCase):

    def setUp(self):
        reconciliation_report_service.clear()

    def test_generate_report(self):

        reconciliation_report_service.record(
            merchant_id="merchant-001",
            reference="PAY-001",
            amount=5000,
            currency="NGN",
        )

        report = reconciliation_report_service.generate(
            "merchant-001"
        )

        self.assertEqual(
            report["merchant_id"],
            "merchant-001"
        )

        self.assertEqual(
            report["total_transactions"],
            1
        )

        self.assertEqual(
            report["total_amount"],
            5000
        )


if __name__ == "__main__":
    unittest.main()
