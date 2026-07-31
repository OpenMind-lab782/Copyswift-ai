from payment_engine.logging.audit import AuditLogger


class WebhookHandler:
    """
    Generic webhook processor.
    Gateway-specific verification will be added later.
    """

    def __init__(self):
        self.audit = AuditLogger()

    def process(self, gateway, payload):
        """
        Process a webhook payload.

        Expected payload example:

        {
            "event": "payment.success",
            "reference": "PAY-001",
            "status": "success"
        }
        """

        event = payload.get("event", "unknown")
        reference = payload.get("reference", "unknown")
        status = payload.get("status", "unknown")

        self.audit.log(
            action="WEBHOOK",
            reference=reference,
            status=status.upper(),
            gateway=gateway,
            details=event
        )

        return {
            "status": "processed",
            "gateway": gateway,
            "event": event,
            "reference": reference
        }
