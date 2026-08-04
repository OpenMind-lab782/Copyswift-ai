from flask import Blueprint, jsonify

frontend_api = Blueprint("frontend_api", __name__)


@frontend_api.route("/frontend/config", methods=["GET"])
def config():

    return jsonify({
        "platform": "CopySwiftAI",
        "version": "5.0.0",
        "authentication": True,
        "assistant": True,
        "checkout": True,
        "dashboard": True,
        "payments": True,
        "status": "ready"
    }), 200
