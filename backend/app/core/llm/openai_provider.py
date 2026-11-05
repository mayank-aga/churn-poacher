"""
OpenAI LLM Provider Implementation.
Supports GPT-4o, GPT-4o-mini, and structured JSON outputs via OpenAI SDK or REST.
"""

import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    """Provider implementation for OpenAI models."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._model = model or settings.OPENAI_MODEL

    @property
    def name(self) -> str:
        return f"openai:{self._model}"

    async def is_available(self) -> bool:
        return bool(self._api_key and len(self._api_key.strip()) > 5)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if not await self.is_available():
            raise RuntimeError("OpenAIProvider is not available (OPENAI_API_KEY is not configured)")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": messages,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        if not await self.is_available():
            raise RuntimeError("OpenAIProvider is not available (OPENAI_API_KEY is not configured)")

        schema = response_model.model_json_schema()
        system = (system_prompt or "") + (
            f"\nYou MUST respond ONLY with valid JSON conforming to the following JSON Schema:\n{json.dumps(schema)}"
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": messages,
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            return response_model.model_validate_json(raw_text)
