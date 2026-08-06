import unittest

from app import app


class ApiKeyAuthenticationTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_missing_api_key(self):
        response = self.client.get("/api/v1/payments")
        self.assertEqual(response.status_code, 401)

    def test_invalid_api_key(self):
        response = self.client.get(
            "/api/v1/payments",
            headers={
                "X-API-Key": "INVALID-KEY"
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_api_key(self):
        merchant = self.client.post(
            "/api/v1/merchants",
            json={
                "name": "CopySwift AI",
                "email": "admin@copyswiftai.com"
            }
        ).get_json()

        response = self.client.get(
            "/api/v1/payments",
            headers={
                "X-API-Key": merchant["api_key"]
            }
        )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
