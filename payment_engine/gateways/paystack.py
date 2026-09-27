import os
from decimal import Decimal, InvalidOperation

import requests

from payment_engine.gateways.base import BaseGateway
from payment_engine.gateway_capabilities import GatewayCapabilities
from payment_engine.provider_mode import ProviderMode
from payment_engine.utils.reference import PaymentReference


class PaystackGateway(BaseGateway):
    """
    Paystack gateway with deterministic MOCK mode and real TEST/LIVE API modes.

    PaymentEngine amounts remain in major currency units. Paystack amounts are
    converted to subunits only at this gateway boundary.
    """

    API_BASE_URL = "https://api.paystack.co"

    def __init__(self, mode=ProviderMode.MOCK, secret_key=None, http_client=None):
        self._mode = (
            ProviderMode(mode.lower())
            if isinstance(mode, str)
            else mode
        )
        self._secret_key = secret_key or os.getenv("PAYSTACK_SECRET_KEY")
        self._http = http_client or requests

    @property
    def name(self):
        return "paystack"

    @property
    def capabilities(self):
        return GatewayCapabilities(
            supports_cards=True,
            supports_bank_transfer=True,
            supports_refunds=True,
        )

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = (
            ProviderMode(mode.lower())
            if isinstance(mode, str)
            else mode
        )

    def _require_real_credentials(self):
        if not self._secret_key:
            raise RuntimeError(
                "PAYSTACK_SECRET_KEY is required for Paystack test/live mode."
            )

        expected_prefix = (
            "sk_test_" if self._mode == ProviderMode.SANDBOX
            else "sk_live_"
        )
        if not self._secret_key.startswith(expected_prefix):
            raise RuntimeError(
                f"Paystack {self._mode.value} mode requires a "
                f"{expected_prefix} secret key."
            )

    @staticmethod
    def _to_subunit(amount):
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError("Paystack amount must be numeric.")

        if value < 0:
            raise ValueError("Paystack amount cannot be negative.")

        subunit = value * Decimal("100")
        if subunit != subunit.to_integral_value():
            raise ValueError(
                "Paystack amount must resolve to a whole subunit."
            )

        return int(subunit)

    def _headers(self):
        self._require_real_credentials()
        return {
            "Authorization": f"Bearer {self._secret_key}",
            "Content-Type": "application/json",
        }

    def _failure(self, message, reference=None):
        result = {
            "status": "failed",
            "gateway": self.name,
            "mode": self._mode.value,
            "message": message,
        }
        if reference:
            result["reference"] = reference
        return result

    def initialize_payment(self, amount, currency, customer, **kwargs):
        reference = kwargs.get("reference", PaymentReference.generate())

        if self._mode == ProviderMode.MOCK:
            return {
                "status": "verified",
                "gateway": self.name,
                "mode": "mock",
                "authorization_url": (
                    f"https://mock.paystack.local/pay/{reference}"
                ),
                "reference": reference,
                "amount": amount,
                "currency": currency,
            }

        customer_email = (
            customer.get("email")
            if isinstance(customer, dict)
            else customer
        )
        if not customer_email:
            raise ValueError(
                "Paystack requires a customer email address."
            )

        payload = {
            "email": customer_email,
            "amount": self._to_subunit(amount),
            "currency": currency,
            "reference": reference,
        }

        response = self._http.post(
            f"{self.API_BASE_URL}/transaction/initialize",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        body = response.json()

        if not response.ok or not body.get("status"):
            return self._failure(
                body.get("message", "Paystack initialization failed."),
                reference,
            )

        data = body.get("data") or {}
        authorization_url = data.get("authorization_url")
        access_code = data.get("access_code")
        returned_reference = data.get("reference", reference)

        if not authorization_url or not access_code or not returned_reference:
            return self._failure(
                "Paystack initialization returned incomplete transaction data.",
                reference,
            )

        return {
            "status": "initialized",
            "gateway": self.name,
            "mode": self._mode.value,
            "authorization_url": authorization_url,
            "access_code": access_code,
            "reference": returned_reference,
            "amount": amount,
            "currency": currency,
        }

    def verify_payment(
        self,
        reference,
        expected_amount=None,
        expected_currency=None,
    ):
        if self._mode == ProviderMode.MOCK:
            return {
                "status": "verified",
                "gateway": self.name,
                "mode": "mock",
                "reference": reference,
                "paid": True,
                "amount": 100,
                "currency": "NGN",
                "customer": "mock@copyswiftai.com",
                "message": "Mock payment verified successfully.",
            }

        response = self._http.get(
            f"{self.API_BASE_URL}/transaction/verify/{reference}",
            headers=self._headers(),
            timeout=30,
        )
        body = response.json()

        if not response.ok or not body.get("status"):
            return self._failure(
                body.get("message", "Paystack verification failed."),
                reference,
            )

        data = body.get("data") or {}

        if data.get("status") != "success":
            return self._failure(
                f"Paystack transaction status is {data.get('status', 'unknown')}.",
                reference,
            )

        if data.get("reference") != reference:
            return self._failure(
                "Paystack verification reference mismatch.",
                reference,
            )

        if expected_currency and str(data.get("currency", "")).upper() != str(
            expected_currency
        ).upper():
            return self._failure(
                "Paystack transaction currency does not match the payment.",
                reference,
            )

        if expected_amount is not None:
            expected_subunit = self._to_subunit(expected_amount)
            if data.get("amount") != expected_subunit:
                return self._failure(
                    "Paystack transaction amount does not match the payment.",
                    reference,
                )

        return {
            "status": "verified",
            "gateway": self.name,
            "mode": self._mode.value,
            "reference": reference,
            "paid": True,
            "amount": expected_amount,
            "currency": expected_currency or data.get("currency"),
            "customer": (data.get("customer") or {}).get("email")
            if isinstance(data.get("customer"), dict)
            else None,
            "message": body.get("message", "Verification successful"),
        }

    def refund_payment(self, reference, amount=None):
        if self._mode == ProviderMode.MOCK:
            return {
                "status": "success",
                "gateway": self.name,
                "mode": "mock",
                "reference": reference,
                "refunded_amount": amount,
                "message": "Mock refund completed.",
            }

        return {
            "status": "unsupported",
            "gateway": self.name,
            "mode": self._mode.value,
            "reference": reference,
            "message": (
                "Real Paystack refunds are not enabled by this scoped patch."
            ),
        }

    def health_check(self):
        if self._mode == ProviderMode.MOCK:
            return {
                "status": "healthy",
                "gateway": self.name,
                "mode": "mock",
            }

        return {
            "status": "configured",
            "gateway": self.name,
            "mode": self._mode.value,
            "credentials_configured": bool(self._secret_key),
        }
