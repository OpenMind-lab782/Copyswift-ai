from datetime import datetime, timezone
from payment_engine.registry import GatewayRegistry
from payment_engine.health import HealthRegistry
from payment_engine.idempotency import IdempotencyManager
from payment_engine.events import EventBus
from payment_engine.subscribers import register_default_subscribers
from payment_engine.middleware import MiddlewareManager
from payment_engine.retry import RetryPolicy
from payment_engine.circuit_breaker import CircuitBreaker
from payment_engine.config import EngineConfig
from payment_engine.metrics import MetricsCollector
from payment_engine.tracing import CorrelationId
from payment_engine.latency import LatencyRecorder, Timer
from payment_engine.health_monitor import GatewayHealthMonitor
from payment_engine.provider_mode import ProviderModeManager
from payment_engine.gateway_config import GatewayConfig
from payment_engine.gateway_factory import GatewayFactory

from payment_engine.gateways.crypto import CryptoGateway
from payment_engine.gateways.paystack import PaystackGateway
from payment_engine.gateways.flutterwave import FlutterwaveGateway
from payment_engine.gateways.dpo import DPOGateway


class PaymentEngine:

    VERSION = "1.2.0"

    def __init__(self, config=None):
        self.config = config or EngineConfig()
        self.metrics = MetricsCollector()
        self.latency = LatencyRecorder()
        self.gateway_health = GatewayHealthMonitor()
        self.started_at = datetime.now(timezone.utc)
        self.registry = GatewayRegistry()
        self.provider_mode = ProviderModeManager()
        self.gateway_config = GatewayConfig()
        self.health = HealthRegistry()
        self.idempotency = IdempotencyManager()
        self.events = EventBus()
        register_default_subscribers(self.events)

        self.middleware = MiddlewareManager()
        self.retry = RetryPolicy(
            retries=self.config.retry_attempts,
            delay=self.config.retry_delay,
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_failure_threshold,
            recovery_timeout=self.config.circuit_recovery_timeout,
        )

        for gateway_name in GatewayFactory.supported_gateways():
            self.registry.register(
                GatewayFactory.create(gateway_name)
            )

        self.gateway_config.configure('crypto')
        self.gateway_config.configure('paystack')
        self.gateway_config.configure('flutterwave')
        self.gateway_config.configure('dpo')

    def gateways(self):
        return self.registry.list()


    def get_provider_mode(self):
        return self.provider_mode.mode

    def set_provider_mode(self, mode):
        self.provider_mode.set_mode(mode)


    def get_gateway_mode(self, gateway_name):
        return self.gateway_config.mode(gateway_name)

    def gateway_capability_report(self):
        report = {}

        for name in self.registry.list():
            gateway = self.registry.get(name)
            caps = getattr(gateway, "capabilities", None)

            report[name] = {} if caps is None else vars(caps)

        return report


    def configure_gateway(self, gateway_name, mode):
        self.gateway_config.configure(gateway_name, mode)




    def get_metrics(self):
        """Return a snapshot of engine metrics."""
        return self.metrics.snapshot()

    def get_latency(self):
        return self.latency.snapshot()


    def get_gateway_health(self):
        return self.gateway_health.snapshot()



    def get_engine_status(self):
        now = datetime.now(timezone.utc)

        return {
            "version": "2.0.0",
            "status": "healthy",
            "started_at": self.started_at.isoformat(),
            "uptime_seconds": int((now - self.started_at).total_seconds()),
            "gateways": len(self.gateways()),
            "metrics": self.get_metrics(),
            "latency": self.get_latency(),
            "gateway_health": self.get_gateway_health(),
        }



    def validate_engine(self):
        status = self.get_engine_status()

        return {
            "ready": (
                status["status"] == "healthy"
                and status["gateways"] > 0
            ),
            "checks": {
                "engine_status": status["status"],
                "registered_gateways": status["gateways"],
                "metrics": True,
                "latency": True,
                "gateway_health": True,
            }
        }


    def get_gateway(self, name):
        gateway = self.registry.get(name)

        if gateway is None:
            raise ValueError(f"Unknown gateway: {name}")

        return gateway



    def submit_payment(self, request):
        gateway = self.get_gateway(request.gateway)

        return gateway.initialize_payment(
            request.amount,
            request.currency,
            request.customer
        )
    def create_payment(
        self,
        gateway,
        amount,
        currency,
        customer
    ):
        context = {
            "gateway": gateway,
            "amount": amount,
            "currency": currency,
            "customer": customer,
        }

        context = self.middleware.before(
            "create_payment",
            context,
        )

        result = self.get_gateway(gateway).initialize_payment(
            amount,
            currency,
            customer
        )

        if isinstance(result, dict):
            self.events.publish(
                "payment_initialized",
                **result,
            )

        result = self.middleware.after(
            "verify_payment",
            context,
            result,
        )

        result = self.middleware.after(
            "create_payment",
            context,
            result,
        )

        result = self.middleware.after(
            "refund_payment",
            context,
            result,
        )

        result = self.middleware.after(
            "handle_webhook",
            context,
            result,
        )

        return result

    def verify_payment(
        self,
        gateway,
        reference
    ):
        self.metrics.increment('verify_requests')
        correlation_id = CorrelationId.new()
        context = {
            "gateway": gateway,
            "reference": reference,
        }

        context = self.middleware.before(
            "verify_payment",
            context,
        )
        if self.idempotency.is_processed(reference):
            duplicate = {
                "status": "duplicate",
                "gateway": gateway,
                "reference": reference,
            }

            self.events.publish(
                "payment_duplicate_detected",
                **duplicate,
            )

            return duplicate

        with Timer() as timer:
            result = self.circuit_breaker.execute(
                self.retry.execute,
                self.get_gateway(gateway).verify_payment,
                reference,
            )

        self.latency.record(gateway, timer.elapsed)

        if (
            isinstance(result, dict)
            and result.get("status") == "verified"
        ):
            self.idempotency.mark_processed(reference)

            self.events.publish(
                "payment_verified",
                **result,
            )

            result["correlation_id"] = correlation_id
            self.gateway_health.record_success(gateway)
            self.metrics.increment("verify_success")

        return result

    def refund_payment(
        self,
        gateway,
        reference
    ):
        context = {
            "gateway": gateway,
            "reference": reference,
        }

        context = self.middleware.before(
            "refund_payment",
            context,
        )
        result = self.get_gateway(gateway).refund_payment(
            reference
        )

        payload = (
            result if isinstance(result, dict)
            else {"result": result}
        )

        payload.setdefault("gateway", gateway)
        payload.setdefault("reference", reference)

        self.events.publish(
            "payment_refunded",
            **payload,
        )

        return result

    def handle_webhook(
        self,
        gateway,
        payload
    ):
        context = {
            "gateway": gateway,
            "payload": payload,
        }

        context = self.middleware.before(
            "handle_webhook",
            context,
        )
        result = self.get_gateway(gateway).handle_webhook(
            payload
        )

        event = {
            "gateway": gateway,
            "success": bool(result),
        }

        self.events.publish(
            "webhook_processed",
            **event,
        )

        return result
