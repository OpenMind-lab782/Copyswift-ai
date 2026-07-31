from tests.base import SwiftEngineTestCase
from payment_engine.utils import error_response


class ErrorResponseTests(SwiftEngineTestCase):

    def test_basic_error(self):
        response = error_response(
            "TEST_ERROR",
            "Something went wrong."
        )

        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "TEST_ERROR")
        self.assertEqual(
            response["error"]["message"],
            "Something went wrong."
        )

    def test_error_with_details(self):
        response = error_response(
            "VALIDATION_ERROR",
            "Invalid input.",
            {"field": "amount"}
        )

        self.assertIn("details", response["error"])


if __name__ == "__main__":
    import unittest
    unittest.main()
