from tests.base import SwiftEngineTestCase

from payment_engine.exceptions import PaymentError
from payment_engine.utils import error_response


class ErrorHandlerTests(SwiftEngineTestCase):

    def test_payment_error_is_swift_error(self):
        error = PaymentError("Example")

        response = error_response(
            error.__class__.__name__,
            str(error)
        )

        self.assertFalse(response["success"])
        self.assertEqual(
            response["error"]["code"],
            "PaymentError"
        )

    def test_internal_error_format(self):
        response = error_response(
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred."
        )

        self.assertEqual(
            response["error"]["code"],
            "INTERNAL_SERVER_ERROR"
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
