import unittest

from payment_engine.openapi import OPENAPI_INFO


class OpenApiMetadataTests(unittest.TestCase):

    def test_metadata_contains_required_fields(self):
        self.assertIn("title", OPENAPI_INFO)
        self.assertIn("version", OPENAPI_INFO)
        self.assertIn("description", OPENAPI_INFO)

    def test_title(self):
        self.assertEqual(
            OPENAPI_INFO["title"],
            "Swift Payment Engine API",
        )


if __name__ == "__main__":
    unittest.main()
