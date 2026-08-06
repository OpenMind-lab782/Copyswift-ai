class PaymentEventRepository:

    def __init__(self):
        self._events = {}

    def save(self, reference, event):

        self._events.setdefault(reference, []).append(event)

        return event

    def list(self, reference):

        return list(
            self._events.get(reference, [])
        )

    def clear(self):

        self._events.clear()
