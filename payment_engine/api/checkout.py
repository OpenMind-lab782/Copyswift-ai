from flask import Blueprint, jsonify, request

from payment_engine.core.checkout_recommender import CheckoutRecommender
from payment_engine.core.checkout_session import CheckoutSessionBuilder
from payment_engine.core.payment_session_bridge import PaymentSessionBridge
from payment_engine.core.payment_engine_adapter import PaymentEngineAdapter

checkout_api = Blueprint("checkout_api", __name__)

recommender = CheckoutRecommender()
builder = CheckoutSessionBuilder()
bridge = PaymentSessionBridge()
adapter = PaymentEngineAdapter()


@checkout_api.route("/checkout", methods=["POST"])
def checkout():

    payload = request.get_json(force=True)

    plan = payload.get("plan", "starter").lower()

    gateway = payload.get("gateway", "paystack").lower()

    recommendation = recommender.recommend(plan)

    session = builder.create(recommendation)

    payment = bridge.create_payment(session)

    result = adapter.execute(
        payment,
        gateway=gateway,
    )

    return jsonify({
        "checkout_session": session,
        "payment": result,
    }), 200
