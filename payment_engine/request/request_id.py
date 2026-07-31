import uuid


def generate_request_id():
    """
    Generate a unique request identifier.
    """
    return str(uuid.uuid4())
