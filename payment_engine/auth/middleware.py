from functools import wraps
from flask import request, jsonify

from payment_engine.auth.api_key import APIKeyManager
from payment_engine.security.rate_limiter import RateLimiter

manager = APIKeyManager()

# Development limits:
# 60 requests per minute per API key
limiter = RateLimiter(limit=60, window=60)


def require_api_key(view):
    """
    Protect Flask endpoints with API key authentication
    and rate limiting.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return jsonify({
                "status": "error",
                "message": "Missing API Key"
            }), 401

        if not manager.validate_key(api_key):
            return jsonify({
                "status": "error",
                "message": "Invalid API Key"
            }), 401

        if not limiter.allow(api_key):
            return jsonify({
                "status": "error",
                "message": "Rate limit exceeded"
            }), 429

        return view(*args, **kwargs)

    return wrapped
