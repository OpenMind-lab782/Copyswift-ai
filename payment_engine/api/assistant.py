from flask import Blueprint, jsonify, request

from payment_engine.core.ai_provider_factory import AIProviderFactory
from payment_engine.core.unified_ai_assistant import UnifiedAIAssistant

assistant_api = Blueprint("assistant_api", __name__)

provider = AIProviderFactory.create()

assistant = UnifiedAIAssistant(
    provider=provider
)


@assistant_api.route("/assistant/chat", methods=["POST"])
def chat():

    payload = request.get_json(silent=True) or {}

    result = assistant.assist(
        customer_name=payload.get("customer", "Guest"),
        intent=payload.get("intent", ""),
        message=payload.get("message", ""),
    )

    return jsonify(result)
