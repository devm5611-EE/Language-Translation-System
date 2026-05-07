import json
import re
import logging
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

DETECT_PROMPT = """Detect the language of the given text. Respond ONLY with valid JSON:
{"language_code": "<ISO 639-1>", "language_name": "<English name>", "confidence": <0.0-1.0>, "script": "<writing script>"}"""

DETECT_PROMPT_SIMPLE = """Detect the language of the given text. You MUST respond with ONLY a JSON object.
Format: {"language_code": "<ISO 639-1>", "language_name": "<English name>", "confidence": <0.0-1.0>, "script": "<writing script>"}

Example: {"language_code": "en", "language_name": "English", "confidence": 0.99, "script": "Latin"}"""


def detect_language(text: str) -> dict:
    """
    Detect the language of given text using Groq API.
    
    Args:
        text: Text to detect language for
        
    Returns:
        Dictionary with language detection results
    """
    client = Groq(api_key=Config.GROQ_API_KEY)
    model = Config.DEFAULT_MODEL
    
    # Determine if model supports JSON mode (verified working models)
    json_mode_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    supports_json_mode = model in json_mode_models
    
    system_prompt = DETECT_PROMPT if supports_json_mode else DETECT_PROMPT_SIMPLE
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f'Detect language of:\n"{text[:500]}"'},
    ]
    
    try:
        if supports_json_mode:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=128,
                    response_format={"type": "json_object"},
                )
            except Exception as json_error:
                logger.warning(f"JSON mode failed for language detection, falling back: {json_error}")
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=128,
                )
        else:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=128,
            )
        
        raw = resp.choices[0].message.content.strip()
        
        # Parse JSON with fallback
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        
        # Fallback response
        logger.warning(f"Could not parse language detection response: {raw[:100]}")
        return {
            "language_code": "unknown",
            "language_name": "Unknown",
            "confidence": 0.0,
            "script": "Unknown"
        }
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise RuntimeError(f"Detection service error: {e}")
