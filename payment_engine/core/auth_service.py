"""
Authentication Service
"""

import secrets


class AuthenticationService:
    """
    Simple token-based authentication service.
    """

    def __init__(self):
        self._tokens = {}

    def login(self, email):
        token = secrets.token_urlsafe(32)
        self._tokens[token] = email
        return {
            "token": token,
            "email": email,
        }

    def authenticate(self, token):
        return self._tokens.get(token)

    def logout(self, token):
        return self._tokens.pop(token, None) is not None
