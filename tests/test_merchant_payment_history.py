import unittest

from app import app
from payment_engine.services import payment_service


class MerchantPaymentHistoryTests(unittest.TestCase):

    def setUp(self):
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

    def test_new_merchant_has_empty_history(self):
        response = self.client.get(
            "/api/v1/payments",
            headers={
                "X-API-Key": self.api_key
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])


if __name__ == "__main__":
    unittest.main()
