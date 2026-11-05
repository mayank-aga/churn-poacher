"""
Google Gemini LLM Provider Implementation.
Supports Gemini 1.5 Flash, Gemini 1.5 Pro, and native JSON output schemas via REST API.
"""

import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Provider implementation for Google Gemini models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = model or settings.GEMINI_MODEL

    @property
    def name(self) -> str:
        return f"gemini:{self._model}"

    async def is_available(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 5)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if not await self.is_available():
            raise RuntimeError("GeminiProvider is not available (GEMINI_API_KEY is not configured)")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError(f"Gemini returned no candidates: {data}")
            return candidates[0]["content"]["parts"][0]["text"]

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        if not await self.is_available():
            raise RuntimeError("GeminiProvider is not available (GEMINI_API_KEY is not configured)")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self._api_key}"
        schema = response_model.model_json_schema()
        
        full_system = (system_prompt or "") + (
            f"\nYou MUST respond strictly in valid JSON format matching this JSON schema:\n{json.dumps(schema)}"
        )

        contents = [
            {"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{full_system}\n\nUSER PROMPT:\n{prompt}"}]}
        ]

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "response_mime_type": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError(f"Gemini returned no candidates: {data}")
            raw_text = candidates[0]["content"]["parts"][0]["text"]
            return response_model.model_validate_json(raw_text)
