from .registry import GatewayRegistry
from .adapter import GatewayAdapter
from .paystack import PaystackGateway
from .flutterwave import FlutterwaveGateway
from .stripe import StripeGateway
from .crypto import CryptoGateway
from .router import GatewayRouter
from .health import GatewayHealthMonitor
from .failover import GatewayFailoverEngine
from .routing import SmartRoutingPolicy
from .engine import RoutingEngine

gateway_registry = GatewayRegistry()

from .metrics import GatewayMetrics

from .weighted_routing import WeightedRoutingStrategy

from .adaptive_engine import AdaptiveRoutingEngine

from .merchant_policy import MerchantRoutingPolicy
from .capability_registry import GatewayCapabilityRegistry
from .webhook_signature import WebhookSignatureVerifier
