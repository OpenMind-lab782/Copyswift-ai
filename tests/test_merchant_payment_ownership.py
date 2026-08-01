import unittest

from app import app


class MerchantPaymentOwnershipTests(unittest.TestCase):

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

    def test_merchants_only_see_their_own_payments(self):

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
                    "email": "customer@example.com",
                    "name": "Customer"
                }
            }
        )

        self.assertEqual(payment.status_code, 201)

        merchant_one_history = self.client.get(
            "/api/v1/payments",
            headers={
                "X-API-Key": self.key_one
            }
        )

        merchant_two_history = self.client.get(
            "/api/v1/payments",
            headers={
                "X-API-Key": self.key_two
            }
        )

        self.assertEqual(len(merchant_one_history.get_json()), 1)
        self.assertEqual(merchant_two_history.get_json(), [])


if __name__ == "__main__":
    unittest.main()
