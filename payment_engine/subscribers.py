from payment_engine.logger import log_payment_event


class LoggingSubscriber:

    def __call__(self, payload):
        log_payment_event(
            "event_bus",
            **payload
        )


class HealthSubscriber:

    def __call__(self, payload):
        # Reserved for future health updates
        return True


class AuditSubscriber:

    def __call__(self, payload):
        log_payment_event(
            "audit",
            **payload
        )


def register_default_subscribers(event_bus):
    """
    Register built-in subscribers.
    """

    logger = LoggingSubscriber()
    health = HealthSubscriber()
    audit = AuditSubscriber()

    event_bus.subscribe("payment_verified", logger)
    event_bus.subscribe("payment_verified", health)
    event_bus.subscribe("payment_verified", audit)

    event_bus.subscribe("payment_initialized", logger)
    event_bus.subscribe("payment_initialized", audit)

    event_bus.subscribe("webhook_processed", logger)
    event_bus.subscribe("webhook_processed", audit)

    return event_bus
