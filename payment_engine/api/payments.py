from flask import Blueprint, jsonify, request, g

from payment_engine.api.auth import require_api_key
from payment_engine.engine import PaymentEngine
from payment_engine.exceptions import ValidationError
from payment_engine.rate_limit import RateLimiter
from payment_engine.services import payment_service

payment_api = Blueprint("payment_api", __name__)

engine = PaymentEngine()
rate_limiter = RateLimiter(limit=60, window=60)


def _client_key():
    return request.headers.get("X-API-Key", request.remote_addr or "anonymous")


def _check_rate_limit():
    try:
        rate_limiter.check(_client_key())
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 429
    return None


@payment_api.route("/payments", methods=["POST"])
@require_api_key
def initialize_payment():
    limited = _check_rate_limit()
    if limited:
        return limited

    data = request.get_json(force=True)

    result = engine.create_payment(
        gateway=data["gateway"],
        amount=data["amount"],
        currency=data["currency"],
        customer=data["customer"],
    )

    merchant = getattr(g, "merchant", None)

    if merchant is not None and isinstance(result, dict):
        result["merchant_id"] = merchant["merchant_id"]

    payment_service.save(result)

    return jsonify(result), 201


@payment_api.route("/payments", methods=["GET"])
@require_api_key
def list_payments():
    limited = _check_rate_limit()
    if limited:
        return limited

    merchant = getattr(g, "merchant", None)
    payments = payment_service.list()

    if merchant is not None:
        merchant_id = merchant.get("merchant_id")
        payments = [
            payment
            for payment in payments
            if payment.get("merchant_id") == merchant_id
        ]

    return jsonify(payments)


@payment_api.route("/payments/<reference>", methods=["GET"])
@require_api_key
def get_payment(reference):
    limited = _check_rate_limit()
    if limited:
        return limited

    payment = payment_service.get(reference)

    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    merchant = getattr(g, "merchant", None)

    if (
        merchant is not None
        and payment.get("merchant_id") != merchant["merchant_id"]
    ):
        return jsonify({"error": "Payment not found"}), 404

    return jsonify(payment)


@payment_api.route("/payments/<reference>/verify", methods=["POST"])
@require_api_key
def verify_payment(reference):
    limited = _check_rate_limit()
    if limited:
        return limited

    payment = payment_service.get(reference)

    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    payment_service.update_status(
        reference,
        "verified",
    )

    return jsonify(payment_service.get(reference))


@payment_api.route("/payments/<reference>/cancel", methods=["POST"])
@require_api_key
def cancel_payment(reference):
    limited = _check_rate_limit()
    if limited:
        return limited

    payment = payment_service.get(reference)

    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    payment_service.update_status(
        reference,
        "cancelled",
    )

    return jsonify(payment_service.get(reference))
