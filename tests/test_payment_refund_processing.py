import unittest

from app import app


class PaymentRefundProcessingTests(unittest.TestCase):

    def setUp(self):
        from payment_engine.services import payment_service

        payment_service.clear()

        self.client = app.test_client()

        merchant = self.client.post(
            "/api/v1/merchants",
            json={
                "name": "CopySwift AI",
                "email": "admin@copyswiftai.com"
            }
        ).get_json()

        self.api_key = merchant["api_key"]

    def test_cannot_refund_another_merchants_payment(self):
        merchant_two = self.client.post(
            "/api/v1/merchants",
            json={"name": "Merchant Two", "email": "two@example.com"},
        ).get_json()
        payment = self.client.post(
            "/api/v1/payments",
            headers={"X-API-Key": self.api_key},
            json={"gateway": "paystack", "amount": 5000, "currency": "NGN", "customer": {"email": "customer@example.com"}},
        ).get_json()
        response = self.client.post(
            f"/api/v1/payments/{payment["reference"]}/refund",
            headers={"X-API-Key": merchant_two["api_key"]},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/payments/{payment["reference"]}", headers={"X-API-Key": self.api_key}).get_json()["status"], payment["status"])

    def test_refund_existing_payment(self):

        payment = self.client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": self.api_key
            },
            json={
                "gateway": "paystack",
                "amount": 5000,
                "currency": "NGN",
                "customer": {
                    "email": "customer@example.com"
                }
            }
        ).get_json()

        response = self.client.post(
            f'/api/v1/payments/{payment["reference"]}/refund',
            headers={
                "X-API-Key": self.api_key
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "refunded"
        )


if __name__ == "__main__":
    unittest.main()
