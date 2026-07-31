from payment_engine.exceptions import ValidationError


def require_fields(data, *fields):
    missing = [field for field in fields if field not in data]

    if missing:
        raise ValidationError(
            "Missing required fields: " + ", ".join(missing)
        )


def validate_positive_amount(amount):
    if amount <= 0:
        raise ValidationError(
            "Amount must be greater than zero."
        )

    return amount
