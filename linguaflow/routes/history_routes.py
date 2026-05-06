from flask import Blueprint, request, jsonify
import logging
from routes._helpers import get_current_user
from models.translation_model import TranslationModel

logger = logging.getLogger(__name__)
history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
def get_history():
    payload, err = get_current_user()
    if err:
        return err

    user_id = payload["sub"]
    try:
        page     = max(1, int(request.args.get("page",     1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 20))))
    except (ValueError, TypeError):
        page, per_page = 1, 20

    source_lang = request.args.get("source_lang", "").strip() or None
    target_lang = request.args.get("target_lang", "").strip() or None
    search      = request.args.get("search",      "").strip() or None
    sort        = request.args.get("sort", "newest")

    try:
        skip  = (page - 1) * per_page
        items = TranslationModel.find_by_user(
            user_id=user_id, skip=skip, limit=per_page,
            source_lang=source_lang, target_lang=target_lang,
            search=search, sort=sort,
        )
        total = TranslationModel.count_by_user(user_id)
        return jsonify({
            "items":    [TranslationModel.to_dict(t) for t in items],
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    max(1, (total + per_page - 1) // per_page),
        }), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("History fetch error")
        return jsonify({"error": f"Could not load history: {str(e)}"}), 500


@history_bp.route("", methods=["DELETE"])
def clear_history():
    payload, err = get_current_user()
    if err:
        return err
    try:
        deleted = TranslationModel.delete_all_by_user(payload["sub"])
        return jsonify({"message": f"Deleted {deleted} translation(s)."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@history_bp.route("/<translation_id>", methods=["DELETE"])
def delete_one(translation_id):
    payload, err = get_current_user()
    if err:
        return err
    try:
        ok = TranslationModel.delete_one(translation_id, payload["sub"])
        if not ok:
            return jsonify({"error": "Translation not found."}), 404
        return jsonify({"message": "Deleted."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@history_bp.route("/stats", methods=["GET"])
def user_stats():
    payload, err = get_current_user()
    if err:
        return err
    try:
        stats = TranslationModel.user_stats_today(payload["sub"])
        return jsonify(stats), 200
    except Exception as e:
        logger.exception("Stats error")
        return jsonify({"count": 0, "avg_confidence": 0, "last_response_time": "—", "total_chars": 0}), 200
