from flask import Blueprint, request, jsonify
import logging
from routes._helpers import get_current_user
from services.translation_service import translate, LANGUAGE_NAMES
from services.detect_service import detect_language
from utils.validators import validate_text_length, sanitize_text
from config import Config

logger = logging.getLogger(__name__)
translate_bp = Blueprint("translate", __name__, url_prefix="/api")


@translate_bp.route("/languages", methods=["GET"])
def get_languages():
    """Public — returns all supported languages sorted by name."""
    langs = sorted(
        [{"code": k, "name": v} for k, v in LANGUAGE_NAMES.items()],
        key=lambda x: x["name"]
    )
    return jsonify({"languages": langs}), 200


@translate_bp.route("/translate", methods=["POST"])
def translate_text():
    payload, err = get_current_user()
    if err:
        return err

    data        = request.get_json(silent=True) or {}
    source_text = sanitize_text(data.get("text") or "")
    target_lang = (data.get("target_lang") or "").strip().lower()
    source_lang = (data.get("source_lang") or "auto").strip().lower()
    model       = data.get("model") or Config.DEFAULT_MODEL

    if not target_lang:
        return jsonify({"error": "target_lang is required."}), 400

    ok, err_msg = validate_text_length(source_text)
    if not ok:
        return jsonify({"error": err_msg}), 400

    if target_lang not in LANGUAGE_NAMES:
        return jsonify({"error": f"Unsupported target language: {target_lang}"}), 400

    try:
        result = translate(
            source_text=source_text,
            target_lang=target_lang,
            user_id=payload["sub"],
            model=model,
            source_lang=source_lang,
        )
        return jsonify(result), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    except Exception as e:
        logger.exception("Translation error")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500


@translate_bp.route("/detect", methods=["POST"])
def detect():
    payload, err = get_current_user()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    text = sanitize_text(data.get("text") or "")

    ok, err_msg = validate_text_length(text)
    if not ok:
        return jsonify({"error": err_msg}), 400

    try:
        result = detect_language(text)
        return jsonify(result), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    except Exception as e:
        logger.exception("Detection error")
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500
