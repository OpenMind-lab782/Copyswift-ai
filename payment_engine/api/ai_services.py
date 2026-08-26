from flask import Blueprint, jsonify, request

from payment_engine.core.ai_provider_factory import AIProviderFactory
from payment_engine.core.market_brain import MarketBrain
from payment_engine.core.market_strategist import MarketStrategist
from payment_engine.core.ai_sales_manager import AISalesManager

ai_services_api = Blueprint("ai_services_api", __name__)

provider = AIProviderFactory.create()

market_brain = MarketBrain(provider=provider)
market_strategist = MarketStrategist(provider=provider)
sales_manager = AISalesManager(provider=provider)


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
