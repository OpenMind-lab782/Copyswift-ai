from flask import Blueprint, jsonify, request

webhook_api = Blueprint("webhook_api", __name__)


@webhook_api.route("/webhooks", methods=["POST"])
def receive_webhook():
    payload = request.get_json(silent=True) or {}

    event = payload.get("event", "unknown")

    return jsonify({
        "success": True,
        "received": True,
        "event": event,
    }), 200
