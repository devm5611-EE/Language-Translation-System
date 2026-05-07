import jwt
import datetime
import sys
import os
import redis
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logger = logging.getLogger(__name__)

# Redis client for token blacklist
_redis_client = None
try:
    _redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _redis_client.ping()
    logger.info("Redis connected for JWT blacklist")
except Exception as e:
    logger.warning(f"Redis unavailable for blacklist: {e}. Using in-memory fallback.")
    _redis_client = None

# In-memory fallback
_memory_blacklist = set()


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
    # Check if token is blacklisted
    if _redis_client:
        if _redis_client.exists(f"blacklist:{token}"):
            raise jwt.InvalidTokenError("Token has been revoked.")
    else:
        if token in _memory_blacklist:
            raise jwt.InvalidTokenError("Token has been revoked.")
    
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def revoke_token(token: str):
    try:
        # Decode to get expiry
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
        exp = payload.get('exp', 0)
        
        # Calculate TTL
        now = datetime.datetime.utcnow().timestamp()
        ttl = int(exp - now) if exp > now else 3600  # Default 1 hour if expired
        
        if _redis_client:
            # Store in Redis with TTL matching token expiry
            _redis_client.setex(f"blacklist:{token}", ttl, "1")
        else:
            # Fallback to memory (cleared on restart)
            _memory_blacklist.add(token)
            
    except jwt.InvalidTokenError:
        # Token already invalid, no need to blacklist
        pass
    except Exception as e:
        logger.error(f"Error revoking token: {e}")


def extract_token(auth_header: str) -> str:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header.")
    return auth_header.split(" ", 1)[1]
