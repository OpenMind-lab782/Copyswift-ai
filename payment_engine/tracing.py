import uuid


class CorrelationId:
    @staticmethod
    def new():
        return str(uuid.uuid4())
