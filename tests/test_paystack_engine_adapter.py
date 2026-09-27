import os
import unittest
from unittest.mock import patch

from payment_engine.engine import PaymentEngine
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.provider_mode import ProviderMode


class FakeResponse:
    def __init__(self, body, ok=True):
        self._body = body
        self.ok = ok

    def json(self):
        return self._body


class FakePaystackHttp:
    def __init__(self, initialize_body=None, verify_body=None):
        self.initialize_body = initialize_body
        self.verify_body = verify_body
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return FakeResponse(self.initialize_body)

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return FakeResponse(self.verify_body)


class PaystackEngineAdapterTests(unittest.TestCase):
    def test_mock_mode_remains_default(self):
        engine = PaymentEngine()
        self.assertEqual(
            engine.get_gateway_mode("paystack"),
            ProviderMode.MOCK,
        )

    def test_sandbox_initialization_converts_major_units_to_subunits(self):
        http = FakePaystackHttp(
            initialize_body={
                "status": True,
                "message": "Authorization URL created",
                "data": {
                    "authorization_url": "https://checkout.paystack.com/test",
                    "access_code": "test-access",
                    "reference": "COPY-TEST-1",
                },
            }
        )
        gateway = PaystackGateway(
            mode=ProviderMode.SANDBOX,
            secret_key="sk_test_unit",
            http_client=http,
        )

        result = gateway.initialize_payment(
            100,
            "NGN",
            {"email": "customer@example.com"},
            reference="COPY-TEST-1",
        )

        self.assertEqual(result["status"], "initialized")
        self.assertEqual(http.post_calls[0][1]["json"]["amount"], 10000)
        self.assertEqual(http.post_calls[0][1]["json"]["currency"], "NGN")

    def test_sandbox_verification_requires_success_amount_and_currency(self):
        http = FakePaystackHttp(
            verify_body={
                "status": True,
                "message": "Verification successful",
                "data": {
                    "status": "success",
                    "reference": "COPY-TEST-1",
                    "amount": 10000,
                    "currency": "NGN",
                },
            }
        )
        gateway = PaystackGateway(
            mode=ProviderMode.SANDBOX,
            secret_key="sk_test_unit",
            http_client=http,
        )

        result = gateway.verify_payment(
            "COPY-TEST-1",
            expected_amount=100,
            expected_currency="NGN",
        )

        self.assertEqual(result["status"], "verified")
        self.assertTrue(result["paid"])

    def test_sandbox_verification_rejects_amount_mismatch(self):
        http = FakePaystackHttp(
            verify_body={
                "status": True,
                "message": "Verification successful",
                "data": {
                    "status": "success",
                    "reference": "COPY-TEST-1",
                    "amount": 9999,
                    "currency": "NGN",
                },
            }
        )
        gateway = PaystackGateway(
            mode=ProviderMode.SANDBOX,
            secret_key="sk_test_unit",
            http_client=http,
        )

        result = gateway.verify_payment(
            "COPY-TEST-1",
            expected_amount=100,
            expected_currency="NGN",
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("amount", result["message"].lower())

    def test_sandbox_verification_rejects_null_currency(self):
        http = FakePaystackHttp(
            verify_body={
                "status": True,
                "message": "Verification successful",
                "data": {
                    "status": "success",
                    "reference": "COPY-TEST-1",
                    "amount": 10000,
                    "currency": None,
                },
            }
        )
        gateway = PaystackGateway(
            mode=ProviderMode.SANDBOX,
            secret_key="sk_test_unit",
            http_client=http,
        )

        result = gateway.verify_payment(
            "COPY-TEST-1",
            expected_amount=100,
            expected_currency="NGN",
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("currency", result["message"].lower())

    def test_sandbox_verification_rejects_missing_data(self):
        http = FakePaystackHttp(
            verify_body={
                "status": True,
                "message": "Verification successful",
            }
        )
        gateway = PaystackGateway(
            mode=ProviderMode.SANDBOX,
            secret_key="sk_test_unit",
            http_client=http,
        )

        result = gateway.verify_payment(
            "COPY-TEST-1",
            expected_amount=100,
            expected_currency="NGN",
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("status", result["message"].lower())

    def test_sensitive_payment_fields_are_redacted_from_logs(self):
        with patch("payment_engine.logger.logger.info") as mock_info:
            from payment_engine.logger import log_payment_event

            log_payment_event(
                "payment_initialized",
                authorization_url="https://checkout.paystack.com/secret",
                access_code="secret-access-code",
                customer="customer@example.com",
                reference="COPY-TEST-1",
                amount=100,
                currency="NGN",
            )

        message = mock_info.call_args.args[0]
        self.assertNotIn("https://checkout.paystack.com/secret", message)
        self.assertNotIn("secret-access-code", message)
        self.assertNotIn("customer@example.com", message)
        self.assertEqual(message.count("[REDACTED]"), 3)
        self.assertIn("reference=COPY-TEST-1", message)
        self.assertIn("amount=100", message)

    def test_engine_initialization_uses_retry_policy(self):
        class FailingGateway:
            def __init__(self):
                self.calls = 0

            def initialize_payment(self, amount, currency, customer):
                self.calls += 1
                raise RuntimeError("transport failure")

        engine = PaymentEngine(payment_service=object())
        gateway = FailingGateway()

        with patch.object(engine, "get_gateway", return_value=gateway):
            with self.assertRaises(RuntimeError):
                engine.create_payment(
                    "paystack",
                    100,
                    "NGN",
                    {"email": "customer@example.com"},
                )

        self.assertEqual(
            gateway.calls,
            engine.config.retry_attempts,
        )

    def test_engine_can_select_sandbox_without_changing_default(self):
        with patch.dict(
            os.environ,
            {
                "PAYSTACK_ENGINE_MODE": "sandbox",
            },
            clear=False,
        ):
            engine = PaymentEngine()

        self.assertEqual(
            engine.get_gateway_mode("paystack"),
            ProviderMode.SANDBOX,
        )
        self.assertEqual(
            engine.get_gateway("paystack").mode,
            ProviderMode.SANDBOX,
        )


if __name__ == "__main__":
    unittest.main()
