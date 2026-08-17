from payment_engine.factory import RepositoryFactory


class PaymentEventService:

    def __init__(self, repository=None):
        self.repository = (
            repository
            or RepositoryFactory.payment_event_repository()
        )

    def record(
        self,
        reference,
        event,
        status,
        timestamp,
        metadata=None,
        connection=None,
    ):
        return self.repository.save(
            reference,
            {
                "event": event,
                "status": status,
                "timestamp": timestamp,
                "metadata": metadata or {},
            },
            connection=connection,
        )

    def has_verified_event(self, reference):
        return self.repository.has_verified_event(
            reference
        )

    def list(self, reference):
        return self.repository.list(reference)

    def clear(self):
        return self.repository.clear()


payment_event_service = PaymentEventService()
