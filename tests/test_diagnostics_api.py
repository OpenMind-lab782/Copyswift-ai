import unittest

from app import app


class DiagnosticsApiTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_diagnostics_endpoint(self):

        response = self.client.get("/diagnostics")

        self.assertEqual(response.status_code, 200)

        body = response.get_json()

        self.assertIn("status", body)
        self.assertIn("version", body)
        self.assertIn("services", body)

        self.assertEqual(body["status"], "ok")

        self.assertIsInstance(
            body["services"],
            dict
        )


if __name__ == "__main__":
    unittest.main()
