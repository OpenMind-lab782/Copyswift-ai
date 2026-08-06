from functools import wraps

from flask import jsonify, request, g

from payment_engine.services import merchant_service

service = merchant_service


def require_api_key(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return jsonify({
                "error": "Missing API key"
            }), 401

        merchant = service.authenticate(api_key)

        if merchant is None:
            return jsonify({
                "error": "Invalid API key"
            }), 401

        g.merchant = merchant

        return view(*args, **kwargs)

    return wrapper
