"""
LLM Provider Abstraction Package.
"""

from app.core.llm.base import BaseLLMProvider
from app.core.llm.factory import get_llm_provider, get_active_provider_status
from app.core.llm.fallback_provider import DeterministicFallbackProvider
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.gemini_provider import GeminiProvider
from app.core.llm.claude_provider import ClaudeProvider
from app.core.llm.services import LLMIntelligenceService
from app.core.llm.schemas import (
    SignalAnalysisResult,
    EvidenceExtractionResult,
    CompanySummaryResult,
    MigrationExplanationResult,
    PersonalizedOutreachResult,
)

__all__ = [
    "BaseLLMProvider",
    "get_llm_provider",
    "get_active_provider_status",
    "DeterministicFallbackProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "LLMIntelligenceService",
    "SignalAnalysisResult",
    "EvidenceExtractionResult",
    "CompanySummaryResult",
    "MigrationExplanationResult",
    "PersonalizedOutreachResult",
]
