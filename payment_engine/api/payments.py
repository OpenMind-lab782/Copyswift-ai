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

    idempotency_key = request.headers.get("Idempotency-Key")

    existing = None

    merchant = getattr(g, "merchant", None)
    merchant_id = (
        merchant.get("merchant_id")
        if merchant is not None
        else None
    )

    idempotency_fingerprint = None

    if idempotency_key and merchant_id:
        import hashlib
        import json

        fingerprint_payload = {
            "gateway": data.get("gateway"),
            "amount": data.get("amount"),
            "currency": data.get("currency"),
            "customer": data.get("customer"),
        }

        canonical_payload = json.dumps(
            fingerprint_payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        idempotency_fingerprint = hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

        existing = payment_service.find_by_idempotency_key(
            merchant_id,
            idempotency_key,
        )

        if existing is not None:
            existing_fingerprint = existing.get(
                "idempotency_fingerprint"
            )

            if (
                existing_fingerprint
                and existing_fingerprint != idempotency_fingerprint
            ):
                return jsonify({
                    "error": (
                        "Idempotency-Key has already been used "
                        "with a different payment request"
                    ),
                    "reference": existing.get("reference"),
                }), 409

            return jsonify(existing), 200

    if existing is not None:
        return jsonify(existing), 200

    result = engine.create_payment(
        gateway=data["gateway"],
        amount=data["amount"],
        currency=data["currency"],
        customer=data["customer"],
    )

    if merchant is not None and isinstance(result, dict):
        result["merchant_id"] = merchant_id

    if idempotency_key:
        result["idempotency_key"] = idempotency_key
        result["idempotency_fingerprint"] = idempotency_fingerprint

    print("=" * 60)
    print("PAYMENT BEFORE SAVE")
    print("=" * 60)
    print(result)

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


@payment_api.route("/payments/<reference>/events", methods=["GET"])
@require_api_key
def get_payment_events(reference):
    limited = _check_rate_limit()
    if limited:
        return limited

    payment = payment_service.get(reference)

    if payment is None:
        return jsonify({"events": []}), 200

    merchant = getattr(g, "merchant", None)

    if (
        merchant is not None
        and payment.get("merchant_id") != merchant["merchant_id"]
    ):
        return jsonify({"events": []}), 200

    return jsonify({
        "reference": reference,
        "events": payment.get("events", [])
    })


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


@payment_api.route("/payments/<reference>/refund", methods=["POST"])
@require_api_key
def refund_payment(reference):
    limited = _check_rate_limit()
    if limited:
        return limited

    payment = payment_service.get(reference)

    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    payment_service.update_status(
        reference,
        "refunded",
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


