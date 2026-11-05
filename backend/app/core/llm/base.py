"""
Base LLM Provider Interface.
Defines abstract contracts for multi-provider language model integration.
"""

from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface for all LLM providers (OpenAI, Gemini, Claude, Fallback)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the identifier of the provider."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks whether the provider has valid credentials and is ready to process requests."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generates raw text response."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """Generates structured output validated against a Pydantic model."""
        pass
