"""
CopySwiftAI™ Shared Ecosystem Kernel.

Provides a stable integration facade over existing ecosystem services
without duplicating their implementations.
"""

from payment_engine.core.ai_manager import AIServiceManager
from payment_engine.core.ai_provider_factory import AIProviderFactory
from payment_engine.core.ai_sales_manager import AISalesManager
from payment_engine.core.market_brain import MarketBrain
from payment_engine.core.market_strategist import MarketStrategist
from payment_engine.core.unified_ai_assistant import UnifiedAIAssistant
from payment_engine.engine import PaymentEngine
from ecosystem_core.product_registry import ProductRegistry


class EcosystemKernel:
    """Shared composition root for CopySwiftAI™ ecosystem products."""

    def __init__(self):
        self.products = ProductRegistry()

        self.products.register(
            "copyswiftai",
            {
                "name": "CopySwiftAI™",
                "type": "platform",
                "status": "active",
                "version": "current",
            },
        )
        self.products.register(
            "seo_agent",
            {
                "name": "CopySwiftAI™ SEO Agent",
                "type": "product",
                "status": "planned",
                "version": "0.1.0",
            },
        )
        self.products.register(
            "document_studio",
            {
                "name": "CopySwiftAI™ Document Studio",
                "type": "product",
                "status": "planned",
                "version": "0.1.0",
            },
        )
        self.ai_provider = AIProviderFactory.create()
        self.ai_services = AIServiceManager()

        self.market_brain = MarketBrain(
            provider=self.ai_provider
        )
        self.market_strategist = MarketStrategist(
            provider=self.ai_provider
        )
        self.sales_manager = AISalesManager(
            provider=self.ai_provider
        )

        self.ai_services.register_service(
            "market_brain",
            self.market_brain,
        )
        self.ai_services.register_service(
            "market_strategist",
            self.market_strategist,
        )
        self.ai_services.register_service(
            "sales_manager",
            self.sales_manager,
        )

        self.assistant = UnifiedAIAssistant(
            provider=self.ai_provider,
            sales=self.sales_manager,
            brain=self.market_brain,
            strategist=self.market_strategist,
        )

        self.payment_engine = PaymentEngine()
