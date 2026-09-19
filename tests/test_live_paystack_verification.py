import os
import tempfile
import unittest
from unittest.mock import patch

import app


class LivePaystackVerificationTests(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        self.original_db_path = app.DB_PATH
        self.original_secret = app.PAYSTACK_SECRET
        app.DB_PATH = self.db_file.name
        app.PAYSTACK_SECRET = "test-secret"
        app.init_db()
        self.client = app.app.test_client()

    def tearDown(self):
        app.DB_PATH = self.original_db_path
        app.PAYSTACK_SECRET = self.original_secret
        try:
            os.unlink(self.db_file.name)
        except FileNotFoundError:
            pass

    def seed_purchase(self, ref="PS_TEST_001", email="buyer@example.com"):
        app.save_credit_purchase(
            email, "basic", 100, 15.0, "₦24,000.00", "paystack", ref
        )
        with self.client.session_transaction() as sess:
            sess["pay_ref"] = ref
            sess["pay_email"] = email
        return ref, email

    @staticmethod
    def paystack_success(ref, email, amount=2400000, currency="NGN",
                         returned_reference=None, returned_email=None):
        return {
            "data": {
                "status": "success",
                "reference": ref if returned_reference is None else returned_reference,
                "amount": amount,
                "currency": currency,
                "customer": {
                    "email": email if returned_email is None else returned_email
                },
            }
        }

    def verify(self, payload, ref):
        with patch.object(app, "paystack_verify", return_value=payload), \
             patch.object(app, "send_notification_email", return_value=None):
            return self.client.get("/verify-paystack?reference=" + ref)

    def purchase_status(self, ref):
        with app.get_db() as db:
            row = db.execute(
                "SELECT status FROM credit_purchases WHERE tx_ref=?", (ref,)
            ).fetchone()
        return row["status"] if row else None

    def test_matching_payment_activates_exact_purchase(self):
        ref, email = self.seed_purchase()
        response = self.verify(self.paystack_success(ref, email), ref)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(app.get_credit_balance(email), 100)
        self.assertEqual(self.purchase_status(ref), "activated")

    def test_wrong_amount_does_not_activate(self):
        ref, email = self.seed_purchase()
        self.verify(self.paystack_success(ref, email, amount=1), ref)
        self.assertEqual(app.get_credit_balance(email), 0)
        self.assertEqual(self.purchase_status(ref), "pending")

    def test_wrong_currency_does_not_activate(self):
        ref, email = self.seed_purchase()
        self.verify(self.paystack_success(ref, email, currency="USD"), ref)
        self.assertEqual(app.get_credit_balance(email), 0)
        self.assertEqual(self.purchase_status(ref), "pending")

    def test_wrong_reference_does_not_activate(self):
        ref, email = self.seed_purchase()
        self.verify(
            self.paystack_success(ref, email, returned_reference="OTHER_REF"), ref
        )
        self.assertEqual(app.get_credit_balance(email), 0)
        self.assertEqual(self.purchase_status(ref), "pending")

    def test_wrong_customer_email_does_not_activate(self):
        ref, email = self.seed_purchase()
        self.verify(
            self.paystack_success(
                ref, email, returned_email="attacker@example.com"
            ),
            ref,
        )
        self.assertEqual(app.get_credit_balance(email), 0)
        self.assertEqual(self.purchase_status(ref), "pending")

    def test_duplicate_callback_does_not_add_credits_twice(self):
        ref, email = self.seed_purchase()
        payload = self.paystack_success(ref, email)
        self.verify(payload, ref)
        self.verify(payload, ref)
        self.assertEqual(app.get_credit_balance(email), 100)
        self.assertEqual(self.purchase_status(ref), "activated")


if __name__ == "__main__":
    unittest.main()
