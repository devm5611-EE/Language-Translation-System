import jwt
import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

_blacklist = set()


def create_token(user_id: str, email: str, role: str = "user") -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    if token in _blacklist:
        raise jwt.InvalidTokenError("Token revoked.")
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def revoke_token(token: str):
    _blacklist.add(token)


def extract_token(auth_header: str) -> str:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header.")
    return auth_header.split(" ", 1)[1]
