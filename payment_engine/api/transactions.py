from flask import Blueprint, jsonify, request

from payment_engine.database.database import get_db
from payment_engine.database.repository import TransactionRepository

transactions = Blueprint("transactions", __name__)


@transactions.route("/transactions", methods=["GET"])
def list_transactions():

    page = max(int(request.args.get("page", 1)), 1)
    limit = max(int(request.args.get("limit", 10)), 1)

    gateway = request.args.get("gateway")
    payment_status = request.args.get("status")

    db = next(get_db())

    try:
        repo = TransactionRepository(db)

        records = repo.list_all()

        if gateway:
            records = [
                t for t in records
                if (t.gateway or "").lower() == gateway.lower()
            ]

        if payment_status:
            records = [
                t for t in records
                if (t.status or "").lower() == payment_status.lower()
            ]

        total = len(records)

        start = (page - 1) * limit
        end = start + limit

        records = records[start:end]

        return jsonify({
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "transactions": [
                {
                    "reference": t.reference,
                    "gateway": t.gateway,
                    "amount": t.amount,
                    "currency": t.currency,
                    "payment_status": t.status
                }
                for t in records
            ]
        })

    finally:
        db.close()


@transactions.route("/transactions/<reference>", methods=["GET"])
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
