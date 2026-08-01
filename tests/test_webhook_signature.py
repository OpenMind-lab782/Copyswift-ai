import unittest

from app import app


class WebhookSignatureTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_webhook_requires_valid_signature(self):
        response = self.client.post(
            "/api/v1/webhooks/paystack",
            headers={
                "X-Paystack-Signature": "INVALID"
            },
            json={
                "event": "charge.success"
            }
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
