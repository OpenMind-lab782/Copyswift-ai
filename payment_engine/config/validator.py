import os


class ConfigurationValidator:
    """
    Validates that required environment variables exist.
    """

    def __init__(self, required=None):
        self.required = list(required or [])

    def missing(self):
        return [
            name
            for name in self.required
            if not os.environ.get(name)
        ]

    def validate(self):
        return len(self.missing()) == 0
