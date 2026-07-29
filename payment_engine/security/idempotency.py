class IdempotencyManager:
    """
    Simple in-memory idempotency manager.

    This implementation is suitable for development.
    Later versions will persist keys in the database or Redis.
    """

    def __init__(self):
        self._processed = set()

    def is_duplicate(self, reference):
        return reference in self._processed

    def register(self, reference):
        self._processed.add(reference)

    def clear(self):
        self._processed.clear()
