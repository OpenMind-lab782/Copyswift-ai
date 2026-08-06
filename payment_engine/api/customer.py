from flask import Blueprint, jsonify

customer_api = Blueprint("customer_api", __name__)


@customer_api.route("/customer/profile", methods=["GET"])
def profile():

    return jsonify({
        "customer": {
            "name": "Demo Customer",
            "subscription": "Pro",
            "status": "Active",
        }
    }), 200
