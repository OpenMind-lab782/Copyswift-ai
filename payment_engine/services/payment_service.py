from payment_engine.repositories import (
    payment_repository,
)
from payment_engine.services.payment_event_service import (
    payment_event_service,
)
from payment_engine.transactions import transaction_manager


class PaymentService:

    def save(self, payment):

        result = transaction_manager.execute(
            payment_repository.save,
            payment
        )

        payment_event_service.record(
            payment["reference"],
            "created",
            payment.get("status"),
            payment.get("created_at")
        )

        return result

    def get(self, reference):
        payment = payment_repository.get(reference)

        if payment is None:
            return None

        timeline = [
            {
                "event": "created",
                "status": "created",
                "timestamp": payment.get("created_at")
            }
        ]

        status = payment.get("status")

        if status != "created":
            timeline.append(
                {
                    "event": status,
                    "status": status,
                    "timestamp": payment.get("updated_at")
                }
            )

        payment["timeline"] = timeline

        events = payment_event_service.list(
            payment["reference"]
        )

        if events:
            payment["events"] = events
        else:
            payment["events"] = [
                {
                    "event": item["event"],
                    "status": item["status"],
                    "timestamp": item["timestamp"]
                }
                for item in timeline
            ]

        return payment

    def list(self):
        return payment_repository.list()

    def find_by_idempotency_key(self, key):
        if not key:
            return None

        for payment in self.list():
            if payment.get("idempotency_key") == key:
                return payment

        return None

    def clear(self):
        return payment_repository.clear()

    def update_status(self, reference, status):
        payment = transaction_manager.execute(
            payment_repository.update_status,
            reference,
            status
        )

        if payment is not None:
            payment_event_service.record(
                reference=reference,
                event=status,
                status=status,
                timestamp=payment.get("updated_at"),
                metadata={
                    "source": "payment_service"
                }
            )

        return payment
