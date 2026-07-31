import os


class Settings:

    def __init__(self):
        self.environment = os.getenv("SWIFT_ENV", "development")
        self.database = os.getenv("SWIFT_DATABASE", "swift_payment.db")
        self.gateway_mode = os.getenv("SWIFT_GATEWAY_MODE", "mock")
        self.log_level = os.getenv("SWIFT_LOG_LEVEL", "INFO")

    @property
    def is_production(self):
        return self.environment.lower() == "production"

    @property
    def is_development(self):
        return self.environment.lower() == "development"
