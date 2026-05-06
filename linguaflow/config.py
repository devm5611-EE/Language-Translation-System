import os
from dotenv import load_dotenv

# override=True ensures .env values always win over stale process env vars
load_dotenv(override=True)


class Config:
    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "linguaflow-secret-2024")
    DEBUG = True

    # MongoDB — env var is named "mongodb"
    MONGO_URI = os.getenv("mongodb", "mongodb://localhost:27017/linguaflow")
    DB_NAME = "linguaflow"

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "linguaflow-jwt-secret-2024")
    JWT_EXPIRY_HOURS = 24

    # Groq LLM — env var is named "key"
    GROQ_API_KEY = os.getenv("key", "")

    # Supported Groq models
    SUPPORTED_MODELS = [
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
    ]
    DEFAULT_MODEL = "llama3-70b-8192"

    # Limits
    MAX_TEXT_LENGTH = 5000
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@linguaflow.com")
