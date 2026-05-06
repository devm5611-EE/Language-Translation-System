from flask import Blueprint, request, jsonify
import logging
from routes._helpers import require_admin
from services.analytics_service import get_admin_dashboard, get_all_users
from models.user_model import UserModel

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
def stats():
    payload, err = require_admin()
    if err:
        return err
    try:
        return jsonify(get_admin_dashboard()), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Admin stats error")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users", methods=["GET"])
def users():
    payload, err = require_admin()
    if err:
        return err
    try:
        page     = max(1, int(request.args.get("page",     1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
        return jsonify(get_all_users(page=page, per_page=per_page)), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Admin users error")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    payload, err = require_admin()
    if err:
        return err
    data    = request.get_json(silent=True) or {}
    allowed = {}
    if "role"      in data and data["role"]      in ("user", "admin"):
        allowed["role"]      = data["role"]
    if "is_active" in data and isinstance(data["is_active"], bool):
        allowed["is_active"] = data["is_active"]
    if not allowed:
        return jsonify({"error": "No valid fields."}), 400
    try:
        ok = UserModel.update(user_id, allowed)
        if ok:
            user = UserModel.find_by_id(user_id)
            return jsonify(UserModel.to_public(user)), 200
        return jsonify({"error": "User not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
