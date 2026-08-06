from threading import Lock


class IdempotencyManager:
    """
    Simple in-memory idempotency tracker.
    Prevents duplicate processing of the same payment reference.
    """

    def __init__(self):
        self._processed = set()
        self._lock = Lock()

    def is_processed(self, reference: str) -> bool:
        with self._lock:
            return reference in self._processed

    def mark_processed(self, reference: str):
        with self._lock:
            self._processed.add(reference)

    def reset(self):
        with self._lock:
            self._processed.clear()
