from flask import Blueprint, request, jsonify
import logging
from routes._helpers import get_current_user
from services.auth_service import update_profile, delete_account
from models.user_model import UserModel

logger = logging.getLogger(__name__)
profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("", methods=["GET"])
def get_profile():
    payload, err = get_current_user()
    if err:
        return err
    try:
        user = UserModel.find_by_id(payload["sub"])
        if not user:
            return jsonify({"error": "User not found."}), 404
        return jsonify(UserModel.to_public(user)), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Get profile error")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("", methods=["PUT"])
def update():
    payload, err = get_current_user()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    try:
        updated = update_profile(payload["sub"], data)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Profile update error")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("", methods=["DELETE"])
def delete():
    payload, err = get_current_user()
    if err:
        return err
    try:
        ok = delete_account(payload["sub"])
        if ok:
            return jsonify({"message": "Account deleted."}), 200
        return jsonify({"error": "Could not delete account."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
