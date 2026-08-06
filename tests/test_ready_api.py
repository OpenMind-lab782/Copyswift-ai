import unittest

from app import app


class ReadyApiTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_ready_endpoint(self):

        response = self.client.get("/ready")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertEqual(body["status"], "ready")
        self.assertIn("database", body)
        self.assertIn("version", body)


if __name__ == "__main__":
    unittest.main()
