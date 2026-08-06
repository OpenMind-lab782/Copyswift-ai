class WebhookIdempotencyManager:

    def __init__(self):
        self._processed = set()

    def is_processed(self, event_id):
        return event_id in self._processed

    def mark_processed(self, event_id):
        self._processed.add(event_id)

    def process(self, event_id):
        if self.is_processed(event_id):
            return False

        self.mark_processed(event_id)
        return True
