"""
Knowledge-Aware Sales Conversation Engine
"""

from payment_engine.core.knowledge_loader import KnowledgeLoader


class SalesConversationEngine:

    def __init__(self, provider=None, knowledge=None):
        self.provider = provider
        self.knowledge = knowledge or KnowledgeLoader()

    def reply(self, customer, message):

        text = (message or "").lower()

        platform = self.knowledge.platform()
        features = self.knowledge.features()
        plans = self.knowledge.plans()

        if (
            "copyswiftai" in text
            or "about" in text
        ):

            response = (
                f"{platform['name']} is an AI-powered business platform developed "
                f"by {platform['company']}. It includes features such as "
                + ", ".join(features[:4])
                + "."
            )

        elif (
            "plan" in text
            or "package" in text
            or "subscription" in text
        ):

            response = (
                "Our available plans are: "
                + ", ".join(plan["name"] for plan in plans.values())
                + ". Tell me about your business and I'll recommend the best one."
            )

        elif "feature" in text:

            response = (
                "CopySwiftAI currently provides: "
                + ", ".join(features)
                + "."
            )

        else:

            response = (
                "Tell me more about your business goals so I can recommend "
                "the best solution."
            )

        return {
            "customer": customer,
            "message": message,
            "response": response,
        }
