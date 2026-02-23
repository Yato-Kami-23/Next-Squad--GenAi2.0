import requests
import logging
import json
import re
from config.settings import settings

logger = logging.getLogger(__name__)


# ── Gemini Client ────────────────────────────────────────────────────────────

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def generate(self, prompt: str) -> dict:
        if not self.is_available():
            return {"success": False, "error": "Gemini API key not configured."}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
            }
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "response": text, "provider": "gemini"}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {"success": False, "error": str(e)}


# ── Ollama Client ────────────────────────────────────────────────────────────

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    def is_available(self) -> bool:
        try:
            r = requests.get(self.base_url, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str) -> dict:
        if not self.is_available():
            return {"success": False, "error": "Ollama is not reachable."}

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
            text = response.json().get("response", "")
            return {"success": True, "response": text, "provider": "ollama"}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"success": False, "error": str(e)}


# ── Hybrid AI Client (Gemini → Ollama fallback) ──────────────────────────────

class AIClient:
    def __init__(self):
        self.gemini = GeminiClient()
        self.ollama = OllamaClient()

    def generate(self, prompt: str) -> dict:
        # Try Gemini first
        if self.gemini.is_available():
            logger.info("Using Gemini as primary provider.")
            result = self.gemini.generate(prompt)
            if result["success"]:
                return result
            logger.warning(f"Gemini failed: {result['error']}. Falling back to Ollama.")

        # Fallback to Ollama
        logger.info("Using Ollama as fallback provider.")
        return self.ollama.generate(prompt)

    def health(self) -> dict:
        return {
            "gemini": "ok" if self.gemini.is_available() else "unavailable",
            "ollama": "ok" if self.ollama.is_available() else "unavailable",
        }

    def parse_json_response(self, raw: str) -> dict | None:
        """Strip markdown fences and parse JSON from model response."""
        try:
            clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
            return json.loads(clean)
        except Exception:
            # Try extracting first JSON block
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return None
