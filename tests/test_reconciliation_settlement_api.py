import unittest

from app import app
from payment_engine.services import merchant_service
from payment_engine.services.reconciliation_service import (
    reconciliation_service,
)
from payment_engine.services.reconciliation_report_service import (
    reconciliation_report_service,
)
from payment_engine.services.settlement_service import (
    settlement_service,
)


class ReconciliationSettlementAPITests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

        reconciliation_service.clear()
        reconciliation_report_service.clear()
        settlement_service.clear()

        merchant = merchant_service.create_merchant({
            "name": "Batch66 Merchant",
            "email": "batch66@example.com",
        })

        self.merchant = merchant
        self.api_key = merchant["api_key"]

    def headers(self):
        return {
            "X-API-Key": self.api_key,
        }

    def test_reconciliation_requires_api_key(self):
        response = self.client.get(
            "/api/v1/reconciliation"
        )

        self.assertEqual(response.status_code, 401)

    def test_record_and_list_reconciliation(self):
        response = self.client.post(
            "/api/v1/reconciliation",
            json={"reference": "PAY-B66-001"},
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            "/api/v1/reconciliation",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 200)

        records = response.get_json()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["reference"],
            "PAY-B66-001",
        )
        self.assertEqual(
            records[0]["merchant_id"],
            self.merchant["merchant_id"],
        )

    def test_reconciliation_report_is_merchant_scoped(self):
        reconciliation_report_service.record(
            merchant_id=self.merchant["merchant_id"],
            reference="PAY-B66-002",
            amount=5000,
            currency="NGN",
        )

        response = self.client.get(
            "/api/v1/reconciliation/report",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 200)

        report = response.get_json()

        self.assertEqual(
            report["merchant_id"],
            self.merchant["merchant_id"],
        )
        self.assertEqual(
            report["total_transactions"],
            1,
        )
        self.assertEqual(
            report["total_amount"],
            5000,
        )

    def test_settlement_requires_required_fields(self):
        response = self.client.post(
            "/api/v1/settlements",
            json={"reference": "PAY-B66-003"},
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_record_and_list_settlement(self):
        response = self.client.post(
            "/api/v1/settlements",
            json={
                "reference": "PAY-B66-004",
                "amount": 7500,
                "currency": "NGN",
            },
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            "/api/v1/settlements",
            headers=self.headers(),
        )

        self.assertEqual(response.status_code, 200)

        settlements = response.get_json()

        self.assertEqual(len(settlements), 1)
        self.assertEqual(
            settlements[0]["reference"],
            "PAY-B66-004",
        )
        self.assertEqual(
            settlements[0]["merchant_id"],
            self.merchant["merchant_id"],
        )


if __name__ == "__main__":
    unittest.main()
