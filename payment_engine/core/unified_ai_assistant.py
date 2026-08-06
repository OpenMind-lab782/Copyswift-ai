"""
Unified AI Assistant
"""

from payment_engine.core.ai_sales_manager import AISalesManager
from payment_engine.core.sales_conversation import SalesConversationEngine
from payment_engine.core.market_brain import MarketBrain
from payment_engine.core.market_strategist import MarketStrategist
from payment_engine.core.decision_engine import DecisionEngine
from payment_engine.core.knowledge_loader import KnowledgeLoader
from payment_engine.core.customer_journey import CustomerJourneyEngine
from payment_engine.core.checkout_recommender import CheckoutRecommender


class UnifiedAIAssistant:

    def __init__(self):
        self.sales = AISalesManager()
        self.chat = SalesConversationEngine()
        self.brain = MarketBrain()
        self.strategist = MarketStrategist()
        self.decision = DecisionEngine()
        self.knowledge = KnowledgeLoader()
        self.journey = CustomerJourneyEngine()
        self.checkout = CheckoutRecommender()

    def assist(self, customer_name, intent, message):

        sales = self.sales.assist({
            "name": customer_name,
            "intent": intent,
        })

        conversation = self.chat.reply(
            customer_name,
            message,
        )

        analysis = self.brain.analyze({
            "trend": "bullish",
            "confidence": 0.95,
            "summary": "Positive market outlook."
        })

        recommendation = self.strategist.recommend(analysis)
        decision = self.decision.decide(recommendation)

        recommended_plan = "starter"
        if intent.lower() == "buy":
            recommended_plan = "pro"

        return {
            "platform": self.knowledge.platform(),
            "plans": self.knowledge.plans(),
            "features": self.knowledge.features(),
            "conversation": conversation,
            "sales": sales,
            "analysis": analysis,
            "recommendation": recommendation,
            "decision": decision,
            "journey": self.journey.journey(intent),
            "checkout": self.checkout.recommend(recommended_plan),
        }
