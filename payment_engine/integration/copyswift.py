from payment_engine.engine import PaymentEngine


class CopySwiftIntegration:

    def __init__(self):
        self.engine = PaymentEngine()

    def initialize_payment(
        self,
        gateway,
        amount,
        currency,
        customer,
    ):
        return self.engine.create_payment(
            gateway=gateway,
            amount=amount,
            currency=currency,
            customer=customer,
        )

    def verify_payment(
        self,
        gateway,
        reference,
    ):
        return self.engine.verify_payment(
            gateway,
            reference,
        )
