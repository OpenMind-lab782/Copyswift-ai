from flask import Blueprint, jsonify

from payment_engine.openapi import OPENAPI_INFO

openapi_api = Blueprint("openapi_api", __name__)


@openapi_api.route("/openapi.json", methods=["GET"])
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": OPENAPI_INFO,
        "paths": {
            "/payments": {
                "get": {
                    "summary": "List payments"
                },
                "post": {
                    "summary": "Create payment"
                }
            },
            "/payments/{reference}": {
                "get": {
                    "summary": "Get payment"
                }
            },
            "/payments/{reference}/verify": {
                "post": {
                    "summary": "Verify payment"
                }
            }
        }
    }

    return jsonify(spec)
