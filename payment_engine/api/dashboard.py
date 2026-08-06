from flask import Blueprint, jsonify

dashboard_api = Blueprint("dashboard_api", __name__)


@dashboard_api.route("/customer/dashboard", methods=["GET"])
def dashboard():

    return jsonify({
        "customer": {
            "name": "Demo Customer",
            "subscription": "Pro",
            "status": "Active"
        },
        "usage": {
            "ai_requests": 24,
            "payments": 3
        },
        "subscription": {
            "plan": "Pro",
            "renewal": "2026-09-01"
        }
    }), 200
