from flask import Blueprint, jsonify

from payment_engine.core.platform import platform_info
from payment_engine.core.knowledge_loader import KnowledgeLoader

system_api = Blueprint("system_api", __name__)

loader = KnowledgeLoader()


@system_api.route("/system", methods=["GET"])
def system():

    return jsonify({
        "platform": platform_info(),
        "features": loader.features(),
        "plans": loader.plans(),
        "status": "ready"
    }), 200
