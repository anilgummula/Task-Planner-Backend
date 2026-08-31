from google import genai
from google.genai import types

from app.config import settings

_client: genai.Client | None = None

SYSTEM_PROMPT = (
    "You are an embedded productivity assistant inside a planner and time-tracking app. "
    "Help the user plan their day, suggest priorities, and summarize their tracked time. "
    "Keep answers short and actionable."
)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def ask_gemini(prompt: str, context: str = "") -> str:
    client = _get_client()
    full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=full_prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return response.text or ""
