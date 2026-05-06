"""
MongoDB connection module.

Uses mongodb+srv:// (Atlas standard) which handles TLS automatically.
The _encode_mongo_uri helper percent-encodes credentials so special
characters in passwords (like @) never break URI parsing.
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
import sys
import os
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

logger = logging.getLogger(__name__)

_client = None
_db     = None


def _encode_mongo_uri(uri: str) -> str:
    """
    Percent-encode username and password in a MongoDB URI.
    Uses rfind('@') to correctly handle passwords that contain '@'.
    """
    scheme_end = uri.find("://")
    if scheme_end == -1:
        return uri

    scheme       = uri[: scheme_end + 3]
    after_scheme = uri[scheme_end + 3:]

    at_pos = after_scheme.rfind("@")
    if at_pos == -1:
        return uri  # no credentials

    credentials = after_scheme[:at_pos]
    hosts_etc   = after_scheme[at_pos + 1:]

    colon_pos = credentials.find(":")
    if colon_pos == -1:
        return uri

    username = credentials[:colon_pos]
    password = credentials[colon_pos + 1:]

    return f"{scheme}{quote_plus(username)}:{quote_plus(password)}@{hosts_etc}"


def get_db():
    global _client, _db
    if _db is None:
        _client = None  # always reset so failed attempts don't cache broken state
        try:
            safe_uri = _encode_mongo_uri(Config.MONGO_URI)

            _client = MongoClient(
                safe_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                tlsAllowInvalidCertificates=True,
            )
            _client.admin.command("ping")
            _db = _client[Config.DB_NAME]
            _create_indexes(_db)
            logger.info("✅ MongoDB Atlas connected successfully.")

        except Exception as e:
            _client = None
            _db     = None
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise RuntimeError(f"Database connection failed: {e}")

    return _db


def _create_indexes(db):
    try:
        db.users.create_index([("email", ASCENDING)],  unique=True, background=True)
        db.users.create_index([("created_at", DESCENDING)],          background=True)
        db.translations.create_index(
            [("user_id", ASCENDING), ("created_at", DESCENDING)],    background=True
        )
        db.translations.create_index([("created_at", DESCENDING)],   background=True)
        logger.info("MongoDB indexes ensured.")
    except Exception as e:
        logger.warning(f"Index creation warning (non-fatal): {e}")
