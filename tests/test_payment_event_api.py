import unittest

from app import app


class PaymentEventApiTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

        merchant = self.client.post(
            "/api/v1/merchants",
            json={
                "name": "CopySwift AI",
                "email": "admin@copyswiftai.com",
            },
        ).get_json()

        self.headers = {
            "X-API-Key": merchant["api_key"],
        }

    def test_payment_events_endpoint_exists(self):

        response = self.client.get(
            "/api/v1/payments/UNKNOWN/events",
            headers=self.headers,
        )

        self.assertNotEqual(
            response.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()
