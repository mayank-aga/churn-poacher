"""
LLM Intelligence Service Functions.
Exposes domain-specific tasks for Signal Analysis, Evidence Extraction,
Company Summarization, Migration Explanation, and Personalized Outreach.
"""

from typing import Optional, Dict, Any, List

from app.core.logging import logger
from app.core.llm.factory import get_llm_provider
from app.core.llm.schemas import (
    SignalAnalysisResult,
    EvidenceExtractionResult,
    CompanySummaryResult,
    MigrationExplanationResult,
    PersonalizedOutreachResult,
)


class LLMIntelligenceService:
    """Provides high-level intelligence generation with automatic provider delegation."""

    @classmethod
    async def analyze_signal(
        cls,
        raw_content: str,
        source: str = "HACKERNEWS",
        provider_name: Optional[str] = None,
    ) -> SignalAnalysisResult:
        """Analyzes a public post for vendor distress, pain points, urgency, and company mentions."""
        provider = get_llm_provider(provider_name)
        prompt = (
            f"Analyze the following public social/forum post from {source} regarding software vendors (especially Datadog):\n\n"
            f"POST CONTENT:\n\"\"\"{raw_content}\"\"\"\n\n"
            f"Classify the complaint category, determine urgency score (0.0 to 1.0), extract pain points, "
            f"and identify any company mentions or technical indicators."
        )
        system_prompt = (
            "You are a Senior B2B Competitive Intelligence Analyst specializing in Cloud & DevOps infrastructure. "
            "Never invent facts or companies. If a company is not explicitly mentioned, leave detected_company_mentions empty."
        )
        try:
            return await provider.generate_structured(
                prompt=prompt,
                response_model=SignalAnalysisResult,
                system_prompt=system_prompt,
            )
        except Exception as e:
            logger.warning(f"LLM signal analysis failed on provider {provider.name}: {e}. Using deterministic fallback.")
            from app.core.llm.fallback_provider import DeterministicFallbackProvider
            return await DeterministicFallbackProvider().generate_structured(
                prompt=prompt,
                response_model=SignalAnalysisResult,
            )

    @classmethod
    async def extract_evidence(
        cls,
        raw_content: str,
        provider_name: Optional[str] = None,
    ) -> EvidenceExtractionResult:
        """Extracts strictly verified claims, complaint specifics, and numerical metrics from text."""
        provider = get_llm_provider(provider_name)
        prompt = (
            f"Extract factual evidence from this user post regarding Datadog:\n\n"
            f"POST CONTENT:\n\"\"\"{raw_content}\"\"\"\n\n"
            f"Separate strictly verified claims from reasonable inferences. Extract any specific cost or volume figures."
        )
        try:
            return await provider.generate_structured(
                prompt=prompt,
                response_model=EvidenceExtractionResult,
            )
        except Exception as e:
            logger.warning(f"LLM evidence extraction failed on provider {provider.name}: {e}. Using deterministic fallback.")
            from app.core.llm.fallback_provider import DeterministicFallbackProvider
            return await DeterministicFallbackProvider().generate_structured(
                prompt=prompt,
                response_model=EvidenceExtractionResult,
            )

    @classmethod
    async def summarize_company_profile(
        cls,
        company_name: str,
        tech_stack: List[str],
        signal_text: str,
        provider_name: Optional[str] = None,
    ) -> CompanySummaryResult:
        """Generates an executive briefing explaining why the target account is ripe for migration."""
        provider = get_llm_provider(provider_name)
        prompt = (
            f"Company Name: {company_name}\n"
            f"Observed Tech Stack: {', '.join(tech_stack) if tech_stack else 'Kubernetes, Cloud Infrastructure'}\n"
            f"Verified Incident/Complaint Text:\n\"\"\"{signal_text}\"\"\"\n\n"
            f"Generate an executive briefing explaining their business scale, current observability dissatisfaction, "
            f"and why an open standard migration to SigNoz or Grafana fits their needs."
        )
        try:
            return await provider.generate_structured(
                prompt=prompt,
                response_model=CompanySummaryResult,
            )
        except Exception as e:
            logger.warning(f"LLM company summary failed on provider {provider.name}: {e}. Using deterministic fallback.")
            from app.core.llm.fallback_provider import DeterministicFallbackProvider
            return await DeterministicFallbackProvider().generate_structured(
                prompt=prompt,
                response_model=CompanySummaryResult,
            )

    @classmethod
    async def explain_migration(
        cls,
        company_name: str,
        current_setup: Dict[str, Any],
        target_backend: str = "SigNoz Cloud",
        provider_name: Optional[str] = None,
    ) -> MigrationExplanationResult:
        """Explains the zero-code OpenTelemetry migration architecture in compelling engineering terms."""
        provider = get_llm_provider(provider_name)
        prompt = (
            f"Company: {company_name}\n"
            f"Target Backend: {target_backend}\n"
            f"Current Setup: {current_setup}\n\n"
            f"Provide a natural language engineering explanation of the OpenTelemetry port 8126 dual-shipping architecture. "
            f"Highlight zero code changes, elimination of host taxes, and zero-loss risk mitigation."
        )
        try:
            return await provider.generate_structured(
                prompt=prompt,
                response_model=MigrationExplanationResult,
            )
        except Exception as e:
            logger.warning(f"LLM migration explanation failed on provider {provider.name}: {e}. Using deterministic fallback.")
            from app.core.llm.fallback_provider import DeterministicFallbackProvider
            return await DeterministicFallbackProvider().generate_structured(
                prompt=prompt,
                response_model=MigrationExplanationResult,
            )

    @classmethod
    async def polish_personalized_outreach(
        cls,
        company_name: str,
        baseline_body: str,
        verified_savings_usd: float,
        target_backend: str = "SigNoz Cloud",
        provider_name: Optional[str] = None,
    ) -> PersonalizedOutreachResult:
        """Polishes executive sales copy while strictly locking financial figures to prevent hallucinations."""
        provider = get_llm_provider(provider_name)
        prompt = (
            f"Company: {company_name}\n"
            f"Target Challenger: {target_backend}\n"
            f"Locked Annual Savings: ${verified_savings_usd:,.2f}\n"
            f"Baseline Draft:\n\"\"\"{baseline_body}\"\"\"\n\n"
            f"Refine the draft into high-empathy, executive-level B2B outreach. "
            f"CRITICAL RULE: DO NOT change, exaggerate, or invent financial figures. Use exact locked savings."
        )
        try:
            return await provider.generate_structured(
                prompt=prompt,
                response_model=PersonalizedOutreachResult,
            )
        except Exception as e:
            logger.warning(f"LLM outreach polish failed on provider {provider.name}: {e}. Using deterministic fallback.")
            from app.core.llm.fallback_provider import DeterministicFallbackProvider
            return await DeterministicFallbackProvider().generate_structured(
                prompt=prompt,
                response_model=PersonalizedOutreachResult,
            )
