class IdempotencyStore:
    """
    Simple in-memory idempotency store.

    Prevents duplicate processing of the same request.
    """

    def __init__(self):
        self._keys = set()

    def register(self, key):
        if key in self._keys:
            return False

        self._keys.add(key)
        return True

    def clear(self):
        self._keys.clear()
