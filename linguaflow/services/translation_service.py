"""
Translation Service
===================
Uses Groq LLM with structured JSON prompts + few-shot examples.
Redis cache is optional — gracefully skipped if unavailable.
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
    _redis = _redis_lib.from_url("redis://localhost:6379", decode_responses=True, socket_connect_timeout=1)
    _redis.ping()
    logger.info("Redis cache connected.")
except Exception:
    _redis = None
    logger.info("Redis unavailable — cache disabled.")


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

FEW_SHOT = [
    {"role": "user", "content": 'Translate to French:\n"Hello, how are you today?"'},
    {"role": "assistant", "content": '{"translation": "Bonjour, comment allez-vous aujourd\'hui ?", "confidence": 0.99, "detected_source_lang": "en"}'},
    {"role": "user", "content": 'Translate to Spanish:\n"The quick brown fox jumps over the lazy dog."'},
    {"role": "assistant", "content": '{"translation": "El rápido zorro marrón salta sobre el perro perezoso.", "confidence": 0.98, "detected_source_lang": "en"}'},
]


def translate(source_text: str, target_lang: str, user_id: str,
              model: str = None, source_lang: str = "auto") -> dict:
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

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *FEW_SHOT,
                {"role": "user", "content": user_msg}]

    # Call Groq
    client = Groq(api_key=Config.GROQ_API_KEY)
    t0 = int(time.time() * 1000)
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages, temperature=0.1, max_tokens=2048,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error(f"Groq error: {e}")
        raise RuntimeError(f"Translation service error: {e}")

    response_time_ms = int(time.time() * 1000) - t0
    parsed = _parse_json(resp.choices[0].message.content.strip())

    detected = parsed.get("detected_source_lang", source_lang or "unknown")
    translation = parsed.get("translation", "")
    confidence = float(parsed.get("confidence", 0.85))

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
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return {"translation": raw, "confidence": 0.5, "detected_source_lang": "unknown"}
