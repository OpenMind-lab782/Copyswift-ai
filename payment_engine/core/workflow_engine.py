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

    def __init__(self):
        self.brain = MarketBrain()
        self.strategist = MarketStrategist()
        self.decision_engine = DecisionEngine()

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
