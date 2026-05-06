import json
import re
import logging
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

DETECT_PROMPT = """Detect the language of the given text. Respond ONLY with valid JSON:
{"language_code": "<ISO 639-1>", "language_name": "<English name>", "confidence": <0.0-1.0>, "script": "<writing script>"}"""


def detect_language(text: str) -> dict:
    client = Groq(api_key=Config.GROQ_API_KEY)
    messages = [
        {"role": "system", "content": DETECT_PROMPT},
        {"role": "user", "content": f'Detect language of:\n"{text[:500]}"'},
    ]
    try:
        resp = client.chat.completions.create(
            model=Config.DEFAULT_MODEL, messages=messages,
            temperature=0.0, max_tokens=128,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except Exception:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                return json.loads(m.group())
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise RuntimeError(f"Detection service error: {e}")
    return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0, "script": "Unknown"}
