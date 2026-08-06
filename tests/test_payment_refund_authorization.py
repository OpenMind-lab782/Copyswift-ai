import unittest

from app import app


class PaymentRefundAuthorizationTests(unittest.TestCase):

    def setUp(self):
        from payment_engine.services import payment_service

        payment_service.clear()

        self.client = app.test_client()

    def test_refund_requires_api_key(self):
        response = self.client.post(
            "/api/v1/payments/UNKNOWN-REFERENCE/refund"
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
