"""REST API server for LLM configuration"""
from flask import Flask, request, jsonify
from flask_cors import CORS

from .llm.llm_router import get_router

app = Flask(__name__)
CORS(app)

@app.route('/api/llm/config', methods=['GET'])
def get_config():
    router = get_router()
    return jsonify(router._config)

@app.route('/api/llm/config', methods=['POST'])
def save_config():
    data = request.json
    router = get_router()
    router.configure(
        provider=data['provider'],
        api_key=data['api_key'],
        base_url=data.get('base_url'),
    )
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
