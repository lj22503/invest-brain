from flask import Blueprint, request, jsonify
from .llm_router import get_router

bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@bp.route('/config', methods=['GET'])
def get_config():
    router = get_router()
    return jsonify(router._config)

@bp.route('/config', methods=['POST'])
def save_config():
    data = request.json
    router = get_router()
    router.configure(
        provider=data['provider'],
        api_key=data['api_key'],
        base_url=data.get('base_url'),
    )
    return jsonify({"status": "ok"})
