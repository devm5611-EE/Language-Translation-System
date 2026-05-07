import logging
from models.user_model import UserModel
from utils.password_hash import hash_password, verify_password
from utils.jwt_handler import create_token
from utils.validators import validate_email, validate_password, validate_name
from utils.audit_logger import log_auth_event
from config import Config

logger = logging.getLogger(__name__)


def register_user(name: str, email: str, password: str, ip_address: str = None) -> dict:
    ok, err = validate_name(name)
    if not ok:
        raise ValueError(err)
    if not validate_email(email):
        raise ValueError("Invalid email address.")
    ok, err = validate_password(password)
    if not ok:
        raise ValueError(err)
    if UserModel.find_by_email(email):
        raise ValueError("An account with this email already exists.")

    role = "admin" if email.lower() == Config.ADMIN_EMAIL.lower() else "user"
    hashed = hash_password(password)
    user_id = UserModel.create(name, email, hashed, role)
    user = UserModel.find_by_id(user_id)
    token = create_token(user_id, email, role)
    
    # Audit log
    log_auth_event("REGISTER", user_id, email, success=True, ip_address=ip_address)
    
    logger.info(f"User registered successfully")
    return {"token": token, "user": UserModel.to_public(user)}


def login_user(email: str, password: str, ip_address: str = None) -> dict:
    user = UserModel.find_by_email(email)
    if not user:
        log_auth_event("LOGIN_FAILED", "unknown", email, success=False, ip_address=ip_address)
        raise ValueError("Invalid email or password.")
    if not user.get("is_active", True):
        log_auth_event("LOGIN_FAILED", str(user["_id"]), email, success=False, ip_address=ip_address)
        raise ValueError("Account deactivated.")
    if not verify_password(password, user["password"]):
        log_auth_event("LOGIN_FAILED", str(user["_id"]), email, success=False, ip_address=ip_address)
        raise ValueError("Invalid email or password.")
    token = create_token(str(user["_id"]), email, user.get("role", "user"))
    
    # Audit log
    log_auth_event("LOGIN_SUCCESS", str(user["_id"]), email, success=True, ip_address=ip_address)
    
    logger.info(f"User logged in successfully")
    return {"token": token, "user": UserModel.to_public(user)}


def update_profile(user_id: str, updates: dict) -> dict:
    clean = {}
    if "name" in updates and updates["name"]:
        ok, err = validate_name(updates["name"])
        if not ok:
            raise ValueError(err)
        clean["name"] = updates["name"].strip()
    if "email" in updates and updates["email"]:
        if not validate_email(updates["email"]):
            raise ValueError("Invalid email.")
        existing = UserModel.find_by_email(updates["email"])
        if existing and str(existing["_id"]) != user_id:
            raise ValueError("Email already in use.")
        clean["email"] = updates["email"].lower().strip()
    if "password" in updates and updates["password"]:
        ok, err = validate_password(updates["password"])
        if not ok:
            raise ValueError(err)
        clean["password"] = hash_password(updates["password"])
    if "preferences" in updates and isinstance(updates["preferences"], dict):
        clean["preferences"] = updates["preferences"]
    if not clean:
        raise ValueError("No valid fields to update.")
    UserModel.update(user_id, clean)
    return UserModel.to_public(UserModel.find_by_id(user_id))


def delete_account(user_id: str) -> bool:
    from models.translation_model import TranslationModel
    TranslationModel.delete_all_by_user(user_id)
    return UserModel.delete(user_id)
