import unittest

from app import app


class PaymentRetrievalNotFoundTests(unittest.TestCase):

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

    def test_lookup_unknown_payment(self):
        response = self.client.get(
            "/api/v1/payments/UNKNOWN-REFERENCE",
            headers={
                "X-API-Key": self.api_key
            }
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
