import unittest

from app import app


class PaymentEventStoreTests(unittest.TestCase):

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

    def test_payment_contains_event_history(self):

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

        response = self.client.get(
            f'/api/v1/payments/{payment["reference"]}',
            headers={
                "X-API-Key": self.api_key
            }
        )

        body = response.get_json()

        self.assertIn("events", body)
        self.assertIsInstance(body["events"], list)
        self.assertGreaterEqual(len(body["events"]), 1)
        self.assertEqual(
            body["events"][0]["event"],
            "created"
        )


if __name__ == "__main__":
    unittest.main()
