"""
AI Workflow Engine
"""

from payment_engine.core.market_brain import MarketBrain
from payment_engine.core.market_strategist import MarketStrategist
from payment_engine.core.decision_engine import DecisionEngine


class AIWorkflowEngine:
    """
    Executes the complete AI intelligence workflow.
    """

    def __init__(
        self,
        provider=None,
        brain=None,
        strategist=None,
        decision_engine=None,
    ):
        self.provider = provider
        self.brain = brain or MarketBrain(provider=provider)
        self.strategist = strategist or MarketStrategist(provider=provider)
        self.decision_engine = decision_engine or DecisionEngine(
            provider=provider
        )

    def execute(self, market_data):
        analysis = self.brain.analyze(market_data)

        recommendation = self.strategist.recommend(
            analysis
        )

        decision = self.decision_engine.decide(
            recommendation
        )

        return {
            "analysis": analysis,
            "recommendation": recommendation,
            "decision": decision,
        }
