from payment_engine.repositories import payment_event_repository


class PaymentEventService:

    def record(
        self,
        reference,
        event,
        status,
        timestamp
    ):
        return payment_event_repository.save(
            reference,
            {
                "event": event,
                "status": status,
                "timestamp": timestamp,
            },
        )

    def list(self, reference):
        return payment_event_repository.list(reference)

    def clear(self):
        return payment_event_repository.clear()


payment_event_service = PaymentEventService()
