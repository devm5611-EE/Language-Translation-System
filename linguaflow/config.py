import os
import secrets
from dotenv import load_dotenv

# override=True ensures .env values always win over stale process env vars
load_dotenv(override=True)


class Config:
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("FLASK_SECRET_KEY environment variable is required. Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # MongoDB
    MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("mongodb")
    if not MONGO_URI:
        raise ValueError("MONGODB_URI environment variable is required")
    DB_NAME = "linguaflow"

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")
    if not JWT_SECRET:
        raise ValueError("JWT_SECRET environment variable is required. Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

    # Groq LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("key")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is required")

    # Supported Groq models (verified working as of May 2026)
    SUPPORTED_MODELS = [
        "llama-3.3-70b-versatile",      # Recommended - best quality (NEW)
        "llama-3.1-8b-instant",         # Fast - good for quick translations
    ]
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    # Limits
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@linguaflow.com")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
