from payment_engine.utils.reference import PaymentReference


class PaystackMockAdapter:

    def initialize_payment(self, amount, currency, customer):
        reference = PaymentReference.generate()

        return {
            "status": "verified",
            "gateway": "paystack",
            "mode": "mock",
            "authorization_url":
                f"https://mock.paystack.local/pay/{reference}",
            "reference": reference,
            "amount": amount,
            "currency": currency,
        }

    def verify_payment(self, reference):
        return {
            "status": "verified",
            "gateway": "paystack",
            "mode": "mock",
            "reference": reference,
            "paid": True,
            "amount": 100,
            "currency": "NGN",
            "customer": "mock@copyswiftai.com",
            "message": "Mock payment verified successfully.",
        }
