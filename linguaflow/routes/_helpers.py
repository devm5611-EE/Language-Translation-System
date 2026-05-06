"""Shared auth helpers for all route blueprints."""
import jwt
from flask import request, jsonify
from utils.jwt_handler import decode_token, extract_token


def get_current_user():
    """
    Returns (payload_dict, None) on success.
    Returns (None, error_response_tuple) on failure.
    """
    try:
        token = extract_token(request.headers.get("Authorization", ""))
        payload = decode_token(token)
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Session expired. Please log in again."}), 401)
    except (jwt.InvalidTokenError, ValueError) as e:
        return None, (jsonify({"error": str(e)}), 401)


def require_admin():
    """
    Returns (payload_dict, None) if user is admin.
    Returns (None, error_response_tuple) otherwise.
    """
    payload, err = get_current_user()
    if err:
        return None, err
    if payload.get("role") != "admin":
        return None, (jsonify({"error": "Admin access required."}), 403)
    return payload, None
