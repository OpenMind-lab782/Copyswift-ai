from flask import jsonify

from payment_engine.exceptions import SwiftPaymentError
from payment_engine.utils import error_response


def register_error_handlers(app):

    @app.errorhandler(SwiftPaymentError)
    def handle_swift_payment_error(error):
        return jsonify(
            error_response(
                error.__class__.__name__,
                str(error)
            )
        ), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify(
            error_response(
                "INTERNAL_SERVER_ERROR",
                "An unexpected error occurred."
            )
        ), 500
