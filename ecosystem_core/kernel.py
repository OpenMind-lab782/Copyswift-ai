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
from ecosystem_core.seo_agent import SEOAgent
from ecosystem_core.document_studio import DocumentStudio
from ecosystem_core.document_importer import DocumentImporter
from ecosystem_core.document_parser import DocumentParser
from ecosystem_core.document_renderer import DocumentRenderer
from ecosystem_core.document_renderers.pymupdf_renderer import PyMuPDFRenderer
from ecosystem_core.document_adapters import DocumentAdapterRegistry
from ecosystem_core.market_intelligence.engines import (
    MemoryEngine,
    EvaluationEngine,
    StrategyEngine,
)
from ecosystem_core.market_intelligence.domains.marketing import (
    MARKETING_MEMORY_SCHEMA,
    MARKETING_RUBRIC,
    MARKETING_STRATEGY_SCHEMA,
)


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
        self.seo_agent = SEOAgent(provider=self.ai_provider)
        self.document_importer = DocumentImporter()
        self.document_adapter_registry = DocumentAdapterRegistry()
        self.document_parser = DocumentParser(
            adapter_registry=self.document_adapter_registry
        )
        self.document_renderer = DocumentRenderer(
            engine=PyMuPDFRenderer()
        )
        self.document_studio = DocumentStudio(
            provider=self.ai_provider,
            importer=self.document_importer,
            parser=self.document_parser,
            renderer=self.document_renderer,
        )
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
        self.ai_services.register_service(
            "seo_agent",
            self.seo_agent,
        )

        self.assistant = UnifiedAIAssistant(
            provider=self.ai_provider,
            sales=self.sales_manager,
            brain=self.market_brain,
            strategist=self.market_strategist,
        )

        # Marketing-domain Market Intelligence services - distinct
        # from payment_engine.core'''s trading-domain MarketBrain and
        # MarketStrategist (self.market_brain / self.market_strategist
        # below, unrelated). These are generic engines specialized
        # for marketing via a schema, reusable by other ecosystem
        # products via their own schemas in the future.
        self.marketing_brain = MemoryEngine(
            schema=MARKETING_MEMORY_SCHEMA,
            provider=self.ai_provider,
        )
        self.marketing_manager = EvaluationEngine(
            rubric=MARKETING_RUBRIC,
            provider=self.ai_provider,
        )
        self.marketing_strategist = StrategyEngine(
            schema=MARKETING_STRATEGY_SCHEMA,
            provider=self.ai_provider,
        )

        self.ai_services.register_service(
            "marketing_brain",
            self.marketing_brain,
        )
        self.ai_services.register_service(
            "marketing_manager",
            self.marketing_manager,
        )
        self.ai_services.register_service(
            "marketing_strategist",
            self.marketing_strategist,
        )

        self.payment_engine = PaymentEngine()


    def register_document_adapter(self, file_format, adapter):
        """Register a document parser adapter with the shared registry."""

        if self.document_parser.adapter_registry is None:
            raise RuntimeError(
                "Document adapter registry is not configured."
            )

        self.document_parser.adapter_registry.register(
            file_format,
            adapter,
        )
