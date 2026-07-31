import unittest

from payment_engine.deployment import ProductionValidator


class ProductionValidatorTests(unittest.TestCase):

    def test_report_exists(self):
        report = ProductionValidator.report()

        self.assertIn("python", report)
        self.assertIn("database", report)
        self.assertIn("environment", report)

    def test_ready_returns_boolean(self):
        self.assertIsInstance(
            ProductionValidator.ready(),
            bool,
        )


if __name__ == "__main__":
    unittest.main()
