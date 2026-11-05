"""
LLM Provider Factory.
Inspects configuration and active credentials to instantiate the appropriate provider.
"""

from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import logger
from app.core.llm.base import BaseLLMProvider
from app.core.llm.fallback_provider import DeterministicFallbackProvider
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.gemini_provider import GeminiProvider
from app.core.llm.claude_provider import ClaudeProvider


def get_llm_provider(requested_provider: Optional[str] = None) -> BaseLLMProvider:
    """
    Returns an instantiated LLM provider based on preference and credential availability.
    Falls back gracefully to DeterministicFallbackProvider when credentials are not configured.
    """
    target = (requested_provider or settings.LLM_PROVIDER or "auto").lower().strip()

    if target == "openai":
        provider = OpenAIProvider()
        return provider

    if target == "gemini":
        provider = GeminiProvider()
        return provider

    if target == "claude" or target == "anthropic":
        provider = ClaudeProvider()
        return provider

    if target == "fallback" or target == "deterministic":
        return DeterministicFallbackProvider()

    # "auto" mode: prioritize configured providers
    gemini = GeminiProvider()
    if gemini._api_key:
        return gemini

    openai = OpenAIProvider()
    if openai._api_key:
        return openai

    claude = ClaudeProvider()
    if claude._api_key:
        return claude

    return DeterministicFallbackProvider()


async def get_active_provider_status() -> Dict[str, Any]:
    """Returns the operational status of all supported LLM providers."""
    providers = {
        "gemini": GeminiProvider(),
        "openai": OpenAIProvider(),
        "claude": ClaudeProvider(),
        "fallback": DeterministicFallbackProvider(),
    }

    status = {}
    active_name = "deterministic-fallback"

    for key, p in providers.items():
        is_avail = await p.is_available()
        status[key] = {
            "name": p.name,
            "available": is_avail,
        }
        if is_avail and active_name == "deterministic-fallback" and key != "fallback":
            active_name = p.name

    return {
        "active_provider": active_name,
        "configured_default": settings.LLM_PROVIDER,
        "providers": status,
    }
