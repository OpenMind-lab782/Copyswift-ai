import unittest

from payment_engine.exceptions import ValidationError
from payment_engine.validation import (
    require_fields,
    validate_positive_amount,
)


class ValidationTests(unittest.TestCase):

    def test_require_fields_success(self):
        require_fields(
            {
                "amount": 100,
                "currency": "NGN",
            },
            "amount",
            "currency",
        )

    def test_require_fields_failure(self):
        with self.assertRaises(ValidationError):
            require_fields({}, "amount")

    def test_positive_amount_success(self):
        validate_positive_amount(100)

    def test_positive_amount_failure(self):
        with self.assertRaises(ValidationError):
            validate_positive_amount(0)


if __name__ == "__main__":
    unittest.main()
