from payment_engine.factory import RepositoryFactory
from payment_engine.services.payment_event_service import (
    payment_event_service,
)
from payment_engine.transactions import transaction_manager


class PaymentService:

    def __init__(
        self,
        payment_repository=None,
        payment_event_service=None,
    ):
        self.payment_repository = (
            payment_repository
            or RepositoryFactory.payment_repository()
        )
        self.payment_event_service = (
            payment_event_service
            or __import__(
                "payment_engine.services.payment_event_service",
                fromlist=["payment_event_service"],
            ).payment_event_service
        )

    def save(self, payment):

        result = transaction_manager.execute(
            self.payment_repository.save,
            payment
        )

        self.payment_event_service.record(
            payment["reference"],
            "created",
            payment.get("status"),
            payment.get("created_at")
        )

        return result

    def get(self, reference):
        payment = self.payment_repository.get(reference)

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

        events = self.payment_event_service.list(
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
        return self.payment_repository.list()

    def find_by_idempotency_key(self, merchant_id, key):
        if not merchant_id or not key:
            return None

        return self.payment_repository.find_by_idempotency_key(
            merchant_id,
            key,
        )

    def clear(self):
        return self.payment_repository.clear()

    def update_status(self, reference, status):
        payment = transaction_manager.execute(
            self.payment_repository.update_status,
            reference,
            status
        )

        if payment is not None:
            self.payment_event_service.record(
                reference=reference,
                event=status,
                status=status,
                timestamp=payment.get("updated_at"),
                metadata={
                    "source": "payment_service"
                }
            )

        return payment
