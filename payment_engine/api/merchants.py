from flask import Blueprint, jsonify, request

from payment_engine.services import merchant_service
from payment_engine.api.auth import require_api_key

merchant_api = Blueprint("merchant_api", __name__)

service = merchant_service


@merchant_api.route("/merchants", methods=["POST"])
def create_merchant():
    data = request.get_json(force=True)

    merchant = service.create_merchant(data)

    return jsonify(merchant), 201


@merchant_api.route("/merchants", methods=["GET"])
@require_api_key
def list_merchants():
    return jsonify(service.list_merchants())


@merchant_api.route("/merchants/<merchant_id>", methods=["GET"])
@require_api_key
def get_merchant(merchant_id):
    merchant = service.get_merchant(merchant_id)

    if merchant is None:
        return jsonify({"error": "Merchant not found"}), 404

    return jsonify(merchant)
