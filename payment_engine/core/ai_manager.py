"""
AI Service Manager
"""

from payment_engine.core.ai_registry import AIServiceRegistry


class AIServiceManager:
    def __init__(self):
        self.registry = AIServiceRegistry()

    def register_service(self, name, service):
        self.registry.register(name, service)

    def get_service(self, name):
        return self.registry.get(name)

    def list_services(self):
        return self.registry.list_services()

    def has_service(self, name):
        return self.registry.registered(name)
