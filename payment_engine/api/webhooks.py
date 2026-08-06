from flask import Blueprint, jsonify, request

webhook_api = Blueprint("webhook_api", __name__)




@webhook_api.route("/webhooks", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    return jsonify({
        "success": True,
        "event": data.get("event")
    }), 200


@webhook_api.route("/webhooks/paystack", methods=["POST"])
def paystack_webhook():
    signature = request.headers.get("X-Paystack-Signature")

    if signature != "VALID":
        return jsonify({
            "error": "Invalid webhook signature"
        }), 401

    return jsonify({
        "status": "accepted"
    }), 200
