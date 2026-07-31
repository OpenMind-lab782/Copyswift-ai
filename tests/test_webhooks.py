import unittest

from flask import Flask

from payment_engine.api.webhooks import webhook_api


class WebhookTests(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(webhook_api)

        self.client = app.test_client()

    def test_webhook_endpoint(self):
        response = self.client.post(
            "/webhooks",
            json={
                "event": "payment.success"
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertEqual(
            data["event"],
            "payment.success",
        )


if __name__ == "__main__":
    unittest.main()
