from flask import Blueprint, jsonify

from payment_engine.auth.middleware import require_api_key

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
@require_api_key
def health():

    return jsonify({
        "status": "healthy",
        "version": "2.4.2",
        "service": "Swift Payment Engine"
    })
