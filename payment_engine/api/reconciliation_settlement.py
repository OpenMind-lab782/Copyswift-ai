from flask import Blueprint, jsonify, request, g

from payment_engine.api.auth import require_api_key
from payment_engine.services.reconciliation_service import (
    reconciliation_service,
)
from payment_engine.services.reconciliation_report_service import (
    reconciliation_report_service,
)
from payment_engine.services.settlement_service import (
    settlement_service,
)


reconciliation_settlement_api = Blueprint(
    "reconciliation_settlement_api",
    __name__,
)


def _merchant_id():
    merchant = getattr(g, "merchant", None)

    if not isinstance(merchant, dict):
        return None

    return merchant.get("merchant_id")


def _json_body():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


@reconciliation_settlement_api.route(
    "/reconciliation",
    methods=["POST"],
)
@require_api_key
def record_reconciliation():
    merchant_id = _merchant_id()

    if not merchant_id:
        return jsonify({"error": "Merchant context unavailable"}), 500

    data = _json_body()

    if data is None:
        return jsonify({"error": "JSON request body required"}), 400

    reference = data.get("reference")

    if not reference:
        return jsonify({"error": "reference is required"}), 400

    record = reconciliation_service.record(
        merchant_id=merchant_id,
        reference=reference,
    )

    return jsonify(record), 201


@reconciliation_settlement_api.route(
    "/reconciliation",
    methods=["GET"],
)
@require_api_key
def list_reconciliation():
    merchant_id = _merchant_id()

    if not merchant_id:
        return jsonify({"error": "Merchant context unavailable"}), 500

    records = reconciliation_service.list(merchant_id)

    return jsonify(records), 200


@reconciliation_settlement_api.route(
    "/reconciliation/report",
    methods=["GET"],
)
@require_api_key
def reconciliation_report():
    merchant_id = _merchant_id()

    if not merchant_id:
        return jsonify({"error": "Merchant context unavailable"}), 500

    report = reconciliation_report_service.generate(merchant_id)

    return jsonify(report), 200


@reconciliation_settlement_api.route(
    "/settlements",
    methods=["POST"],
)
@require_api_key
def record_settlement():
    merchant_id = _merchant_id()

    if not merchant_id:
        return jsonify({"error": "Merchant context unavailable"}), 500

    data = _json_body()

    if data is None:
        return jsonify({"error": "JSON request body required"}), 400

    required = ("reference", "amount", "currency")

    missing = [
        field
        for field in required
        if data.get(field) is None
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing,
        }), 400

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return jsonify({
            "error": "amount must be numeric"
        }), 400

    if amount <= 0:
        return jsonify({
            "error": "amount must be greater than zero"
        }), 400

    settlement = settlement_service.record(
        merchant_id=merchant_id,
        reference=data["reference"],
        amount=amount,
        currency=data["currency"],
    )

    return jsonify(settlement), 201


@reconciliation_settlement_api.route(
    "/settlements",
    methods=["GET"],
)
@require_api_key
def list_settlements():
    merchant_id = _merchant_id()

    if not merchant_id:
        return jsonify({"error": "Merchant context unavailable"}), 500

    settlements = settlement_service.list(merchant_id)

    return jsonify(settlements), 200
