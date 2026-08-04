import os
import unittest

from payment_engine.config.validator import ConfigurationValidator


class ConfigurationValidatorTests(unittest.TestCase):

    def test_missing_required_variable(self):
        os.environ.pop("PAYSTACK_SECRET_KEY", None)

        validator = ConfigurationValidator(
            required=[
                "PAYSTACK_SECRET_KEY",
            ]
        )

        self.assertFalse(
            validator.validate()
        )

    def test_required_variable_present(self):
        os.environ["PAYSTACK_SECRET_KEY"] = "test-key"

        validator = ConfigurationValidator(
            required=[
                "PAYSTACK_SECRET_KEY",
            ]
        )

        self.assertTrue(
            validator.validate()
        )


if __name__ == "__main__":
    unittest.main()
