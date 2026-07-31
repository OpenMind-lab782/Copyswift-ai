from app import app
from tests.base import SwiftEngineTestCase


class APITestCase(SwiftEngineTestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertIn(response.status_code, (200, 404))

    def test_unknown_endpoint(self):
        response = self.client.get("/this-endpoint-does-not-exist")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    import unittest
    unittest.main()
