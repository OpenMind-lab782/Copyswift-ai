from flask import Blueprint, jsonify

index_api = Blueprint("index_api", __name__)


@index_api.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "CopySwiftAI API",
        "version": "5.0.0",
        "status": "ready",
        "endpoints": {
            "system": "/api/v1/system",
            "auth_login": "/api/v1/auth/login",
            "auth_logout": "/api/v1/auth/logout",
            "assistant": "/api/v1/assistant/chat",
            "customer_profile": "/api/v1/customer/profile",
            "customer_dashboard": "/api/v1/customer/dashboard",
            "checkout": "/api/v1/checkout",
            "payments": "/api/v1/payments",
            "merchants": "/api/v1/merchants"
        }
    }), 200
