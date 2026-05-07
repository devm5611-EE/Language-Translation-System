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
# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging based on environment
if os.getenv("FLASK_DEBUG", "False").lower() == "true":
    log_level = logging.DEBUG
    log_handlers = [
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, "app.log")),
    ]
else:
    # Production logging - less verbose, stdout only for Render
    log_level = logging.INFO
    log_handlers = [logging.StreamHandler()]

logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    
    # Load configuration with better error handling
    try:
        app.config.from_object(Config)
        logger.info("Configuration loaded successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        # In production, we might want to continue with defaults for some values
        if not os.getenv("FLASK_DEBUG", "False").lower() == "true":
            logger.warning("Running with minimal configuration due to missing environment variables")
            # Set minimal required config
            app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key-change-in-production')
        else:
            raise

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
    
    # ── Diagnostic endpoint for deployment debugging ──────────────────────────
    @app.route("/diagnostic")
    def diagnostic():
        """Diagnostic page to help debug deployment issues"""
        import os
        import sys
        
        info = {
            "app_status": "running",
            "python_version": sys.version,
            "flask_debug": app.debug,
            "static_folder": app.static_folder,
            "static_url_path": app.static_url_path,
            "template_folder": app.template_folder,
            "environment": {
                "FLASK_DEBUG": os.getenv("FLASK_DEBUG"),
                "MONGODB_URI": "***" if os.getenv("MONGODB_URI") else "NOT SET",
                "GROQ_API_KEY": "***" if os.getenv("GROQ_API_KEY") else "NOT SET",
                "REDIS_URL": "***" if os.getenv("REDIS_URL") else "NOT SET",
            },
            "static_files_exist": {
                "css/style.css": os.path.exists(os.path.join(app.static_folder, "css", "style.css")),
                "js/main.js": os.path.exists(os.path.join(app.static_folder, "js", "main.js")),
                "js/auth.js": os.path.exists(os.path.join(app.static_folder, "js", "auth.js")),
            },
            "routes": [str(rule) for rule in app.url_map.iter_rules()],
        }
        
        return jsonify(info), 200

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
        # Relaxed CSP for production - allow inline styles and scripts needed for the app
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        return response
    
    # HTTPS enforcement - only for local development
    # Render handles HTTPS termination, so we don't need to enforce it in the app
    @app.before_request
    def enforce_https():
        # Only enforce HTTPS in local development when not using a reverse proxy
        if app.debug and not request.is_secure and not request.headers.get('X-Forwarded-Proto'):
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    return app


# Create the WSGI application object for Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
