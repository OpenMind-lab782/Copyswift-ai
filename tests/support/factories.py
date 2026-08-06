class PaymentFactory:

    counter = 1

    @classmethod
    def create(cls, **overrides):

        payment = {
            "reference": f"TEST-{cls.counter:06d}",
            "merchant_id": "merchant-demo",
            "amount": 100,
            "currency": "NGN",
            "status": "pending",
            "gateway": "paystack",
            "customer_email": "customer@example.com",
            "metadata": {}
        }

        payment.update(overrides)

        cls.counter += 1

        return payment
