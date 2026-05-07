import logging
import os
import sys

# Ensure the linguaflow directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

    # CORS — restrict to allowed origins from environment
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # Rate limiting - use in-memory storage if Redis is unavailable
    try:
        import redis
        redis_client = redis.from_url(Config.REDIS_URL, socket_connect_timeout=2)
        redis_client.ping()
        # Redis is available, use it for rate limiting
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=Config.RATELIMIT_STORAGE_URL
        )
        logger.info("Rate limiting configured with Redis backend")
    except Exception as e:
        # Redis unavailable, use in-memory storage
        logger.warning(f"Redis unavailable for rate limiting: {e}. Using in-memory storage.")
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://"
        )

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

    # ── Health check with dependency status ───────────────────────────────────
    @app.route("/health")
    def health():
        from datetime import datetime
        from groq import Groq
        
        checks = {
            "status": "ok",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {}
        }
        
        # Check MongoDB
        try:
            from database.mongodb import get_db
            get_db().admin.command('ping')
            checks["dependencies"]["mongodb"] = "ok"
        except Exception as e:
            checks["dependencies"]["mongodb"] = f"error: {str(e)[:100]}"
            checks["status"] = "degraded"
        
        # Check Redis
        try:
            import redis
            redis_client = redis.from_url(Config.REDIS_URL, socket_connect_timeout=2)
            redis_client.ping()
            checks["dependencies"]["redis"] = "ok"
        except Exception as e:
            checks["dependencies"]["redis"] = f"unavailable: {str(e)[:50]}"
        
        # Check Groq API
        try:
            client = Groq(api_key=Config.GROQ_API_KEY)
            # Don't make actual API call, just validate the key format
            if Config.GROQ_API_KEY and len(Config.GROQ_API_KEY) > 10:
                checks["dependencies"]["groq_api"] = "configured"
            else:
                checks["dependencies"]["groq_api"] = "invalid_key"
                checks["status"] = "degraded"
        except Exception as e:
            checks["dependencies"]["groq_api"] = f"error: {str(e)[:100]}"
            checks["status"] = "degraded"
        
        status_code = 200 if checks["status"] == "ok" else 503
        return jsonify(checks), status_code

    # ── Serve SPA for all non-API routes ─────────────────────────────────────
    @app.route("/")
    @app.route("/<path:path>")
    def index(path=None):
        return render_template("index.html")

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found."}), 404
        return render_template("index.html"), 200

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error."}), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded. Please slow down.",
            "retry_after": str(e.description)
        }), 429
    
    # Handle custom exceptions
    from exceptions import LinguaFlowException
    @app.errorhandler(LinguaFlowException)
    def handle_custom_error(e):
        return jsonify(e.to_dict()), e.status_code

    logger.info("LinguaFlow app created. Routes registered.")
    
    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com"
        return response
    
    # HTTPS enforcement in production
    @app.before_request
    def enforce_https():
        if not app.debug and not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
