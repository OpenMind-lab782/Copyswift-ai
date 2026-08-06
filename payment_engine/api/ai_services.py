from flask import Blueprint, jsonify, request

from payment_engine.core.market_brain import MarketBrain
from payment_engine.core.market_strategist import MarketStrategist
from payment_engine.core.ai_sales_manager import AISalesManager

ai_services_api = Blueprint("ai_services_api", __name__)

market_brain = MarketBrain()
market_strategist = MarketStrategist()
sales_manager = AISalesManager()


@ai_services_api.route("/market-brain", methods=["POST"])
def market_brain_route():

    payload = request.get_json(silent=True) or {}

    return jsonify(
        market_brain.analyze(payload)
    )


@ai_services_api.route("/market-strategist", methods=["POST"])
def market_strategist_route():

    payload = request.get_json(silent=True) or {}

    return jsonify(
        market_strategist.recommend(payload)
    )


@ai_services_api.route("/ai-sales-manager", methods=["POST"])
def ai_sales_manager_route():

    payload = request.get_json(silent=True) or {}

    return jsonify(
        sales_manager.assist(payload)
    )
