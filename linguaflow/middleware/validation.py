"""
Input validation and sanitization middleware.
"""
from flask import request, jsonify
from functools import wraps
import json
import html


MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 10000  # Max text input length


def validate_json_request(f):
    """
    Decorator to validate JSON request body.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Check content type
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json"
                }), 400
            
            # Validate JSON structure
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({
                        "error": "Request body must contain valid JSON"
                    }), 400
            except json.JSONDecodeError as e:
                return jsonify({
                    "error": f"Invalid JSON: {str(e)}"
                }), 400
            
            # Check content length
            content_length = request.content_length
            if content_length and content_length > MAX_CONTENT_LENGTH:
                return jsonify({
                    "error": f"Request body too large. Maximum {MAX_CONTENT_LENGTH // (1024*1024)}MB allowed"
                }), 413
        
        return f(*args, **kwargs)
    
    return decorated_function


def sanitize_input(text):
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return text
    
    # HTML escape
    sanitized = html.escape(text)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_email_format(email):
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import re
    
    if not email:
        return False, "Email is required"
    
    if len(email) > 254:
        return False, "Email address too long"
    
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format"
    
    return True, None


def validate_pagination_params(page, per_page, max_per_page=100):
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum allowed items per page
        
    Returns:
        Tuple of (validated_page, validated_per_page)
    """
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
    except (ValueError, TypeError):
        return 1, 20
    
    # Enforce bounds
    page = max(1, min(page, 10000))  # Max 10k pages
    per_page = max(1, min(per_page, max_per_page))
    
    return page, per_page


def validate_object_id(object_id):
    """
    Validate MongoDB ObjectId format.
    
    Args:
        object_id: String to validate
        
    Returns:
        Boolean indicating if valid
    """
    from bson import ObjectId
    
    if not object_id or not isinstance(object_id, str):
        return False
    
    try:
        ObjectId(object_id)
        return True
    except Exception:
        return False
