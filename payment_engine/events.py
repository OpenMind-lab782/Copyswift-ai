from collections import defaultdict


class EventBus:

    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name, callback):
        self._subscribers[event_name].append(callback)

    def publish(self, event_name, **payload):
        for callback in self._subscribers[event_name]:
            callback(payload)

    def clear(self):
        self._subscribers.clear()
