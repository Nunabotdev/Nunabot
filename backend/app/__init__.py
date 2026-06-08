from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .utils import get_logger

log = get_logger("app")


def create_app(config=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    from .api.bot import bp as bot_bp
    from .api.job import bp as job_bp
    from .api.provider import bp as provider_bp
    from .api.agent import bp as agent_bp
    from .api.market import bp as market_bp

    for bp in (bot_bp, job_bp, provider_bp, agent_bp, market_bp):
        app.register_blueprint(bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "nunabot"})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not found"}), 404

    log.info("Nunabot API ready")
    return app
