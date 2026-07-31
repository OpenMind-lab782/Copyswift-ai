import os


class RenderConfig:

    @staticmethod
    def port():
        return int(os.getenv("PORT", "8080"))

    @staticmethod
    def environment():
        return os.getenv("RENDER_ENV", "development")

    @staticmethod
    def is_production():
        return RenderConfig.environment().lower() == "production"
