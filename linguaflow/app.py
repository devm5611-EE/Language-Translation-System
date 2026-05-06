import logging
import os
import sys

# Ensure the linguaflow directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify
from flask_cors import CORS

from config import Config

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "app.log")),
    ],
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    app.config.from_object(Config)

    # CORS — allow all origins (tighten in production)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register blueprints ───────────────────────────────────────────────────
    from routes.auth_routes import auth_bp
    from routes.translate_routes import translate_bp
    from routes.history_routes import history_bp
    from routes.profile_routes import profile_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"}), 200

    # ── Serve SPA for all non-API routes ─────────────────────────────────────
    @app.route("/")
    @app.route("/<path:path>")
    def index(path=None):
        return render_template("index.html")

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if "/api/" in str(e):
            return jsonify({"error": "Endpoint not found."}), 404
        return render_template("index.html"), 200

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error."}), 500

    logger.info("LinguaFlow app created. Routes registered.")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
