"""
AI Provider Factory
"""

from payment_engine.core.ai_provider import AIProvider


class AIProviderFactory:
    """
    Creates and returns the configured AI provider.
    """

    @staticmethod
    def create():
        return AIProvider()
