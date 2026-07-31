import unittest

from payment_engine.services.crypto_payment_service import CryptoPaymentService


class CryptoPaymentServiceTests(unittest.TestCase):

    def setUp(self):
        self.service = CryptoPaymentService()

    def test_submit(self):
        payment = self.service.submit(
            "TX001",
            {"email": "test@example.com"}
        )

        self.assertEqual(payment["status"], "pending")

    def test_activate(self):
        self.service.submit("TX001", {})

        payment = self.service.activate("TX001")

        self.assertEqual(payment["status"], "activated")

    def test_reject(self):
        self.service.submit("TX001", {})

        payment = self.service.reject("TX001")

        self.assertEqual(payment["status"], "rejected")
