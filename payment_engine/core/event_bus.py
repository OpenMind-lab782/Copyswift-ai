"""
AI Event Bus
"""


class EventBus:
    """
    Simple publish/subscribe event bus.
    """

    def __init__(self):
        self._events = {}

    def subscribe(self, event_name, handler):
        self._events.setdefault(event_name, []).append(handler)

    def publish(self, event_name, payload):
        results = []

        for handler in self._events.get(event_name, []):
            results.append(handler(payload))

        return results

    def subscribers(self, event_name):
        return len(self._events.get(event_name, []))
