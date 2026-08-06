import unittest

from app import app


class PaymentListAuthorizationTests(unittest.TestCase):

    def setUp(self):
        from payment_engine.services import payment_service

        payment_service.clear()

        self.client = app.test_client()

    def test_payment_list_requires_api_key(self):
        response = self.client.get("/api/v1/payments")

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
