class GatewayAdapter:
    """
    Base interface for all payment gateways.
    Every gateway implementation must inherit from this class.
    """

    def initialize_payment(self, payment):
        raise NotImplementedError(
            "initialize_payment() must be implemented."
        )

    def verify_payment(self, reference):
        raise NotImplementedError(
            "verify_payment() must be implemented."
        )

    def refund_payment(self, reference):
        raise NotImplementedError(
            "refund_payment() must be implemented."
        )
