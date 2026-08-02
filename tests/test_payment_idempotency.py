import unittest

from app import app


class PaymentIdempotencyTests(unittest.TestCase):

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

    def test_same_idempotency_key_returns_same_payment(self):
        headers = {
            "X-API-Key": self.api_key,
            "Idempotency-Key": "TEST-IDEMPOTENCY-001"
        }

        payload = {
            "gateway": "paystack",
            "amount": 5000,
            "currency": "NGN",
            "customer": {
                "email": "customer@example.com"
            }
        }

        first = self.client.post(
            "/api/v1/payments",
            headers=headers,
            json=payload
        ).get_json()

        second = self.client.post(
            "/api/v1/payments",
            headers=headers,
            json=payload
        ).get_json()

        self.assertEqual(
            first["reference"],
            second["reference"]
        )


if __name__ == "__main__":
    unittest.main()
