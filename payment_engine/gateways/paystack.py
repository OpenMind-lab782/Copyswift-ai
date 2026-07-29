from payment_engine.base import BaseGateway
from payment_engine.logger import log_payment_event, log_error


class PaystackGateway(BaseGateway):

    name = "paystack"

    def initialize_payment(self, amount, currency, customer):

        log_payment_event(
            "paystack_initialize",
            customer=customer,
            amount=amount,
            currency=currency
        )

        return {
            "success": True,
            "gateway": self.name,
            "status": "initialized"
        }

    def verify_payment(self, reference):

        log_payment_event(
            "paystack_verify",
            reference=reference
        )

        return {
            "success": True,
            "gateway": self.name,
            "status": "verified",
            "reference": reference
        }

    def refund_payment(self, reference):

        return {
            "success": False,
            "message": "Refund not implemented.",
            "reference": reference
        }

    def handle_webhook(self, payload):

        log_payment_event(
            "paystack_webhook",
            payload=bool(payload)
        )

        return {
            "success": True
        }
