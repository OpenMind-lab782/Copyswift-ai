from flask import Blueprint, jsonify, request

from payment_engine.core.auth_service import AuthenticationService

auth_api = Blueprint("auth_api", __name__)

service = AuthenticationService()


@auth_api.route("/auth/login", methods=["POST"])
def login():

    payload = request.get_json(force=True)

    email = payload.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400

    return jsonify(service.login(email)), 200


@auth_api.route("/auth/logout", methods=["POST"])
def logout():

    payload = request.get_json(force=True)

    token = payload.get("token")

    if not token:
        return jsonify({"error": "token is required"}), 400

    return jsonify({
        "success": service.logout(token)
    }), 200
