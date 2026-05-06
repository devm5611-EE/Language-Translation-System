from flask import Blueprint, request, jsonify
import logging
from services.auth_service import register_user, login_user
from utils.jwt_handler import revoke_token, extract_token

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip()
    password =  data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    try:
        result = register_user(name, email, password)
        return jsonify(result), 201

    except ValueError as e:
        # Validation errors (duplicate email, weak password, etc.)
        return jsonify({"error": str(e)}), 409

    except RuntimeError as e:
        # Database connection errors
        logger.error(f"Register DB error: {e}")
        return jsonify({"error": "Database unavailable. Please try again shortly."}), 503

    except Exception as e:
        logger.exception("Register unexpected error")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email    = (data.get("email")    or "").strip()
    password =  data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        result = login_user(email, password)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    except RuntimeError as e:
        logger.error(f"Login DB error: {e}")
        return jsonify({"error": "Database unavailable. Please try again shortly."}), 503

    except Exception as e:
        logger.exception("Login unexpected error")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        token = extract_token(request.headers.get("Authorization", ""))
        revoke_token(token)
    except Exception:
        pass
    return jsonify({"message": "Logged out."}), 200
