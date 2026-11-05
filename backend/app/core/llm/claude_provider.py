"""
Anthropic Claude LLM Provider Implementation.
Supports Claude 3.5 Sonnet, Claude 3 Haiku, and structured JSON outputs via Messages API.
"""

import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class ClaudeProvider(BaseLLMProvider):
    """Provider implementation for Anthropic Claude models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or settings.ANTHROPIC_API_KEY
        self._model = model or settings.ANTHROPIC_MODEL

    @property
    def name(self) -> str:
        return f"claude:{self._model}"

    async def is_available(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 5)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if not await self.is_available():
            raise RuntimeError("ClaudeProvider is not available (ANTHROPIC_API_KEY is not configured)")

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "max_tokens": 2048,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        if not await self.is_available():
            raise RuntimeError("ClaudeProvider is not available (ANTHROPIC_API_KEY is not configured)")

        schema = response_model.model_json_schema()
        system = (system_prompt or "") + (
            f"\nYou MUST output ONLY a valid JSON object matching this schema. Do not include markdown code fences or explanations:\n{json.dumps(schema)}"
        )

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "max_tokens": 2048,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["content"][0]["text"].strip()
            # Clean possible markdown block if wrapped
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return response_model.model_validate_json(raw_text.strip())
