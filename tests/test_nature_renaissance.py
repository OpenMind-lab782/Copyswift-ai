import unittest

from flask import Flask

from nature_renaissance import nature_renaissance_bp


class NatureRenaissancePageTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(nature_renaissance_bp)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_talking_products_page_renders(self):
        response = self.client.get("/nature-renaissance")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Meet the products.", html)
        self.assertIn("Play all products", html)
        self.assertIn("Stop audio", html)
        self.assertIn("Switch to Pidgin", html)
        self.assertIn("data-tab=\"talk\"", html)
        self.assertIn("data-tab=\"voice\"", html)
        self.assertIn("data-tab=\"whatsapp\"", html)
        self.assertIn("Food supplements and herbal products are not medicines", html)

    def test_all_eleven_products_are_configured(self):
        source = open("nature_renaissance.py", encoding="utf-8").read()
        self.assertEqual(source.count('name:"'), 11)
        self.assertIn("https://wa.me/2348064403056", source)


if __name__ == "__main__":
    unittest.main()
