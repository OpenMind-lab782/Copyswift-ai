from flask import Blueprint, jsonify, request

from payment_engine.database.database import get_db
from payment_engine.database.repository import TransactionRepository

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Swift Payment Engine",
        "version": "2.1.0"
    })


@api.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.get_json(silent=True) or {}

    reference = data.get("reference")
    gateway = data.get("gateway", "unknown")

    if not reference:
        return jsonify({
            "status": "error",
            "message": "reference is required"
        }), 400

    db = next(get_db())

    try:
        repo = TransactionRepository(db)

        transaction = repo.get_by_reference(reference)

        if transaction:
            return jsonify({
                "status": "success",
                "verified": True,
                "transaction": {
                    "reference": transaction.reference,
                    "gateway": transaction.gateway,
                    "amount": transaction.amount,
                    "currency": transaction.currency,
                    "payment_status": transaction.status
                }
            })

        return jsonify({
            "status": "success",
            "verified": False,
            "message": "Transaction not found",
            "reference": reference,
            "gateway": gateway
        }), 404

    finally:
        db.close()


@api.route("/transactions", methods=["GET"])
def list_transactions():

    db = next(get_db())

    try:
        repo = TransactionRepository(db)

        transactions = repo.list_all()

        return jsonify({
            "status": "success",
            "count": len(transactions),
            "transactions": [
                {
                    "reference": t.reference,
                    "gateway": t.gateway,
                    "amount": t.amount,
                    "currency": t.currency,
                    "payment_status": t.status
                }
                for t in transactions
            ]
        })

    finally:
        db.close()


@api.route("/transactions/<reference>", methods=["GET"])
def get_transaction(reference):

    db = next(get_db())

    try:
        repo = TransactionRepository(db)

        transaction = repo.get_by_reference(reference)

        if transaction is None:
            return jsonify({
                "status": "error",
                "message": "Transaction not found"
            }), 404

        return jsonify({
            "status": "success",
            "transaction": {
                "reference": transaction.reference,
                "gateway": transaction.gateway,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "payment_status": transaction.status
            }
        })

    finally:
        db.close()
