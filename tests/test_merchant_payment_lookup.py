import unittest

from app import app


class MerchantPaymentLookupTests(unittest.TestCase):

    def setUp(self):
        from payment_engine.services import payment_service

        payment_service.clear()

        self.client = app.test_client()

        merchant_one = self.client.post(
            "/api/v1/merchants",
            json={
                "name": "Merchant One",
                "email": "one@example.com"
            }
        ).get_json()

        merchant_two = self.client.post(
            "/api/v1/merchants",
            json={
                "name": "Merchant Two",
                "email": "two@example.com"
            }
        ).get_json()

        self.key_one = merchant_one["api_key"]
        self.key_two = merchant_two["api_key"]

    def test_merchant_cannot_access_another_payment(self):

        payment = self.client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": self.key_one
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
                "X-API-Key": self.key_two
            }
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
