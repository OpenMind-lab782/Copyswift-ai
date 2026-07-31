import os
import unittest

from payment_engine.deployment import RenderConfig


class RenderConfigTests(unittest.TestCase):

    def tearDown(self):
        os.environ.pop("PORT", None)
        os.environ.pop("RENDER_ENV", None)

    def test_default_port(self):
        self.assertEqual(RenderConfig.port(), 8080)

    def test_custom_port(self):
        os.environ["PORT"] = "10000"
        self.assertEqual(RenderConfig.port(), 10000)

    def test_production_environment(self):
        os.environ["RENDER_ENV"] = "production"
        self.assertTrue(RenderConfig.is_production())


if __name__ == "__main__":
    unittest.main()
