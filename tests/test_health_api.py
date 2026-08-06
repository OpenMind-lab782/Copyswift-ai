import unittest

from app import app


class HealthApiTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):

        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "ok")

        self.assertIn("version", body)

        self.assertIn("timestamp", body)


if __name__ == "__main__":
    unittest.main()
