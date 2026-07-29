from flask import Blueprint, jsonify, request

from payment_engine.services.merchant_service import MerchantService

merchant_api = Blueprint("merchant_api", __name__)

service = MerchantService()


@merchant_api.route("/merchants", methods=["GET"])
def list_merchants():

    merchants = service.list_merchants()

    return jsonify([
        {
            "name": merchant.name,
            "email": merchant.email,
            "active": merchant.active
        }
        for merchant in merchants
    ])


@merchant_api.route("/merchants/<name>", methods=["GET"])
def get_merchant(name):

    merchant = service.get_merchant(name)

    if merchant is None:
        return jsonify({
            "status": "error",
            "message": "Merchant not found"
        }), 404

    return jsonify({
        "name": merchant.name,
        "email": merchant.email,
        "active": merchant.active
    })


@merchant_api.route("/merchants", methods=["POST"])
def register_merchant():

    data = request.get_json()

    try:
        merchant = service.register_merchant(
            data["name"],
            data["email"]
        )

        return jsonify({
            "status": "success",
            "merchant": {
                "name": merchant.name,
                "email": merchant.email,
                "active": merchant.active
            }
        }), 201

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400
