from payment_engine.logging.audit import AuditLogger
from payment_engine.security.idempotency import IdempotencyManager
from payment_engine.core.retry_manager import RetryManager
from payment_engine.core.dead_letter_queue import DeadLetterQueue


class PaymentOrchestrator:

    def __init__(self, gateway_registry):
        self.gateway_registry = gateway_registry
        self.audit = AuditLogger()
        self.idempotency = IdempotencyManager()
        self.retry = RetryManager(retries=3, delay=1)
        self.dlq = DeadLetterQueue()

    def verify_payment(self, gateway_name, reference):

        if self.idempotency.is_duplicate(reference):
            self.audit.log(
                action="VERIFY",
                reference=reference,
                status="DUPLICATE",
                gateway=gateway_name
            )

            return {
                "status": "duplicate",
                "reference": reference
            }

        gateway = self.gateway_registry.get_gateway(gateway_name)

        try:

            result = self.retry.execute(
                gateway.verify_payment,
                reference
            )

            self.audit.log(
                action="VERIFY",
                reference=reference,
                status="SUCCESS",
                gateway=gateway_name
            )

            return result

        except Exception as exc:

            self.dlq.add(
                operation="VERIFY_PAYMENT",
                reference=reference,
                reason=str(exc)
            )

            self.audit.log(
                action="VERIFY",
                reference=reference,
                status="FAILED",
                gateway=gateway_name,
                details=str(exc)
            )

            return {
                "status": "failed",
                "reference": reference,
                "reason": str(exc)
            }
