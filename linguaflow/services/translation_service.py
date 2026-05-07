"""
Translation Service
===================
Uses Groq LLM with structured JSON prompts + few-shot examples.
Redis cache is optional — gracefully skipped if unavailable.
Supports all Groq models with fallback for models that don't support JSON mode.
"""
import json
import time
import hashlib
import logging
import re

from groq import Groq
from config import Config
from models.translation_model import TranslationModel
from models.user_model import UserModel

logger = logging.getLogger(__name__)

# ── Optional Redis cache ──────────────────────────────────────────────────────
_redis = None
try:
    import redis as _redis_lib
    _redis = _redis_lib.from_url(Config.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _redis.ping()
    logger.info("Redis cache connected.")
except Exception as e:
    _redis = None
    logger.info(f"Redis unavailable — cache disabled: {e}")


def _cache_get(key):
    if not _redis:
        return None
    try:
        v = _redis.get(key)
        return json.loads(v) if v else None
    except Exception:
        return None


def _cache_set(key, data):
    if not _redis:
        return
    try:
        _redis.setex(key, 3600, json.dumps(data))
    except Exception:
        pass


# ── Language map ──────────────────────────────────────────────────────────────
LANGUAGE_NAMES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian",
    "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan",
    "zh": "Chinese", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "ht": "Haitian Creole",
    "ha": "Hausa", "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian",
    "is": "Icelandic", "id": "Indonesian", "ga": "Irish", "it": "Italian",
    "ja": "Japanese", "kn": "Kannada", "kk": "Kazakh", "km": "Khmer",
    "ko": "Korean", "ku": "Kurdish", "lo": "Lao", "la": "Latin",
    "lv": "Latvian", "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese", "mi": "Maori", "mr": "Marathi",
    "mn": "Mongolian", "my": "Myanmar", "ne": "Nepali", "no": "Norwegian",
    "fa": "Persian", "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi",
    "ro": "Romanian", "ru": "Russian", "sr": "Serbian", "si": "Sinhala",
    "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "sw": "Swahili", "sv": "Swedish", "tl": "Filipino", "tg": "Tajik",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek", "vi": "Vietnamese",
    "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
}

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are LinguaFlow, a professional AI translation engine.
Translate the given text accurately and naturally.

Rules:
- Preserve tone, style, and formatting
- Do NOT add explanations or commentary
- Output ONLY valid JSON in this exact format:
{"translation": "<translated text>", "confidence": <0.0-1.0>, "detected_source_lang": "<ISO 639-1 code>"}

Confidence guide: 0.95-1.0 = clear text, 0.80-0.94 = good, 0.60-0.79 = acceptable, <0.60 = uncertain"""

SYSTEM_PROMPT_SIMPLE = """You are LinguaFlow, a professional AI translation engine.
Translate the given text accurately and naturally.

IMPORTANT: You MUST respond with ONLY a JSON object, nothing else.
Format: {"translation": "<translated text>", "confidence": <0.0-1.0>, "detected_source_lang": "<ISO 639-1 code>"}

Example response:
{"translation": "Bonjour, comment allez-vous?", "confidence": 0.99, "detected_source_lang": "en"}"""

FEW_SHOT = [
    {"role": "user", "content": 'Translate to French:\n"Hello, how are you today?"'},
    {"role": "assistant", "content": '{"translation": "Bonjour, comment allez-vous aujourd\'hui ?", "confidence": 0.99, "detected_source_lang": "en"}'},
    {"role": "user", "content": 'Translate to Spanish:\n"The quick brown fox jumps over the lazy dog."'},
    {"role": "assistant", "content": '{"translation": "El rápido zorro marrón salta sobre el perro perezoso.", "confidence": 0.98, "detected_source_lang": "en"}'},
]

# Models that support JSON mode (verified working)
JSON_MODE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# Models that need fallback (don't support JSON mode)
FALLBACK_MODELS = []


def translate(source_text: str, target_lang: str, user_id: str,
              model: str = None, source_lang: str = "auto") -> dict:
    """
    Translate text using Groq API with support for all models.
    
    Args:
        source_text: Text to translate
        target_lang: Target language code (e.g., 'fr', 'es')
        user_id: User ID for tracking
        model: Groq model to use (defaults to DEFAULT_MODEL)
        source_lang: Source language code or 'auto' for auto-detection
        
    Returns:
        Dictionary with translation, confidence, and metadata
    """
    model = model if model in Config.SUPPORTED_MODELS else Config.DEFAULT_MODEL
    target_lang = target_lang.lower().strip()

    # Cache check
    cache_key = "lf:" + hashlib.sha256(f"{source_text}|{target_lang}|{model}".encode()).hexdigest()
    cached = _cache_get(cache_key)
    if cached:
        TranslationModel.create(user_id, source_text, cached["translation"],
                                cached["source_lang"], target_lang,
                                cached["confidence"], model, 0)
        UserModel.increment_count(user_id)
        return {**cached, "cache_hit": True, "response_time_ms": 0}

    # Build prompt
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang.upper())
    if source_lang and source_lang != "auto":
        src_name = LANGUAGE_NAMES.get(source_lang, source_lang.upper())
        user_msg = f'Translate from {src_name} to {target_name}:\n"{source_text}"'
    else:
        user_msg = f'Translate to {target_name}:\n"{source_text}"'

    # Determine if model supports JSON mode
    supports_json_mode = model in JSON_MODE_MODELS
    
    # Build messages
    if supports_json_mode:
        system_prompt = SYSTEM_PROMPT
    else:
        system_prompt = SYSTEM_PROMPT_SIMPLE
    
    messages = [{"role": "system", "content": system_prompt}, *FEW_SHOT,
                {"role": "user", "content": user_msg}]

    # Call Groq - Initialize client with proper parameters
    try:
        client = Groq(api_key=Config.GROQ_API_KEY)
    except TypeError as e:
        logger.error(f"Groq client initialization error: {e}")
        # Fallback: try without extra parameters
        client = Groq(api_key=Config.GROQ_API_KEY)
    
    t0 = int(time.time() * 1000)
    
    try:
        # Try with JSON mode if supported
        if supports_json_mode:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048,
                    response_format={"type": "json_object"},
                )
                logger.info(f"Translation successful with {model} (JSON mode)")
            except Exception as json_error:
                logger.warning(f"JSON mode failed for {model}, falling back to text mode: {json_error}")
                # Fallback to text mode
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2048,
                )
        else:
            # Use text mode for models that don't support JSON
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
            )
            logger.info(f"Translation successful with {model} (text mode)")
            
    except Exception as e:
        logger.error(f"Groq API error with model {model}: {str(e)}")
        raise RuntimeError(f"Translation service error: {str(e)}")

    response_time_ms = int(time.time() * 1000) - t0
    
    # Parse response
    response_text = resp.choices[0].message.content.strip()
    parsed = _parse_json(response_text)

    detected = parsed.get("detected_source_lang", source_lang or "unknown")
    translation = parsed.get("translation", "")
    confidence = float(parsed.get("confidence", 0.85))

    # Validate translation
    if not translation or translation.strip() == "":
        logger.error(f"Empty translation received from {model}")
        raise RuntimeError("Translation service returned empty result")

    result = {
        "translation": translation,
        "source_lang": detected,
        "target_lang": target_lang,
        "confidence": confidence,
        "model_used": model,
        "response_time_ms": response_time_ms,
        "cache_hit": False,
    }

    _cache_set(cache_key, {k: v for k, v in result.items() if k != "cache_hit"})
    TranslationModel.create(user_id, source_text, translation, detected,
                            target_lang, confidence, model, response_time_ms)
    UserModel.increment_count(user_id)
    return result


def _parse_json(raw: str) -> dict:
    """
    Parse JSON from response text with multiple fallback strategies.
    
    Args:
        raw: Raw response text from Groq API
        
    Returns:
        Parsed dictionary with translation data
    """
    # Strategy 1: Try direct JSON parsing
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract JSON object from text
    try:
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # Strategy 3: Try to extract from markdown code blocks
    try:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # Strategy 4: If all else fails, create a response from the raw text
    logger.warning(f"Could not parse JSON from response: {raw[:100]}...")
    return {
        "translation": raw.strip(),
        "confidence": 0.6,
        "detected_source_lang": "unknown"
    }
