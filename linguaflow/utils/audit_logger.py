"""
Audit logging module for tracking user actions and security events.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Create dedicated audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Add file handler for audit logs
import os
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

audit_handler = logging.FileHandler(
    os.path.join(log_dir, "audit.log")
)
audit_handler.setFormatter(logging.Formatter(
    '%(asctime)s [AUDIT] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
audit_logger.addHandler(audit_handler)


def log_audit(
    action: str,
    user_id: Optional[str],
    resource: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    success: bool = True
):
    """
    Log an audit event.
    
    Args:
        action: The action performed (e.g., "LOGIN", "DELETE_ACCOUNT")
        user_id: The user ID performing the action (or "anonymous" if not authenticated)
        resource: The resource being accessed (e.g., "auth", "translation", "profile")
        details: Additional details about the action
        ip_address: Client IP address
        success: Whether the action was successful
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id or "anonymous",
        "resource": resource,
        "success": success,
        "ip_address": ip_address or "unknown"
    }
    
    if details:
        # Sanitize sensitive data
        sanitized_details = {}
        for key, value in details.items():
            # Don't log passwords or tokens
            if key in ['password', 'token', 'api_key', 'secret']:
                sanitized_details[key] = "***REDACTED***"
            else:
                sanitized_details[key] = value
        audit_entry["details"] = sanitized_details
    
    audit_logger.info(json.dumps(audit_entry))


def log_auth_event(event_type: str, user_id: str, email: str, success: bool, ip_address: Optional[str] = None):
    """
    Log authentication-related events.
    
    Args:
        event_type: Type of auth event (LOGIN, LOGOUT, REGISTER, PASSWORD_CHANGE)
        user_id: User ID
        email: User email (will be hashed in logs)
        success: Whether the event was successful
        ip_address: Client IP address
    """
    import hashlib
    
    # Hash email for privacy
    email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
    
    log_audit(
        action=event_type,
        user_id=user_id,
        resource="authentication",
        details={
            "email_hash": email_hash,
            "event_type": event_type
        },
        ip_address=ip_address,
        success=success
    )


def log_data_access(user_id: str, resource_type: str, resource_id: str, action: str, ip_address: Optional[str] = None):
    """
    Log data access events.
    
    Args:
        user_id: User ID accessing the data
        resource_type: Type of resource (translation, user, etc.)
        resource_id: ID of the resource being accessed
        action: Action performed (READ, UPDATE, DELETE)
        ip_address: Client IP address
    """
    log_audit(
        action=f"{action}_{resource_type.upper()}",
        user_id=user_id,
        resource=resource_type,
        details={
            "resource_id": resource_id,
            "action": action
        },
        ip_address=ip_address
    )


def log_admin_action(admin_id: str, action: str, target_user_id: str, details: Optional[Dict[str, Any]] = None):
    """
    Log admin actions.
    
    Args:
        admin_id: Admin user ID
        action: Action performed
        target_user_id: User ID affected by the action
        details: Additional details
    """
    log_audit(
        action=f"ADMIN_{action}",
        user_id=admin_id,
        resource="admin_panel",
        details={
            "target_user_id": target_user_id,
            **(details or {})
        }
    )
