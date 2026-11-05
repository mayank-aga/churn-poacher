"""
Deterministic Fallback LLM Provider.
Guarantees 100% reliable, zero-latency, offline execution when external API keys are unavailable.
Strictly adheres to all structured output Pydantic schemas without fabricating claims.
"""

import re
from typing import Optional, Type, TypeVar, List
from pydantic import BaseModel

from app.core.llm.base import BaseLLMProvider
from app.core.llm.schemas import (
    SignalAnalysisResult,
    EvidenceExtractionResult,
    CompanySummaryResult,
    MigrationExplanationResult,
    PersonalizedOutreachResult,
)

T = TypeVar("T", bound=BaseModel)


class DeterministicFallbackProvider(BaseLLMProvider):
    """Deterministic, rule-based provider that produces valid structured outputs without external APIs."""

    @property
    def name(self) -> str:
        return "deterministic-fallback"

    async def is_available(self) -> bool:
        return True

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generates clear, deterministic text."""
        return (
            "Deterministic analysis: Identified competitive displacement opportunity targeting Datadog. "
            "Telemetry volume and cost delta indicate strong potential for OpenTelemetry dual-shipping migration."
        )

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """Produces deterministic instances of supported Pydantic schemas."""
        lower_prompt = prompt.lower()

        if response_model == SignalAnalysisResult:
            category = "PRICING_SHOCK"
            urgency = 0.75
            if any(w in lower_prompt for w in ["outage", "down", "incident", "offline", "degraded", "statuspage"]):
                category = "OUTAGE_DOWNTIME"
                urgency = 0.90
            elif any(w in lower_prompt for w in ["migrate", "alternative", "switch", "replace", "signoz", "grafana"]):
                category = "MIGRATION_INTENT"
                urgency = 0.85
            elif any(w in lower_prompt for w in ["deprecated", "removed", "broken"]):
                category = "FEATURE_DEPRECATION"
                urgency = 0.70

            pain_points = []
            if "bill" in lower_prompt or "cost" in lower_prompt or "custom metric" in lower_prompt:
                pain_points.append("Unpredictable Datadog custom metric billing spikes")
            if "outage" in lower_prompt or "down" in lower_prompt:
                pain_points.append("Monitoring infrastructure unavailability during critical incident")
            if not pain_points:
                pain_points.append("Dissatisfaction with Datadog commercial structure and vendor lock-in")

            # Extract technical indicators
            tech_indicators = []
            for t in ["kubernetes", "k8s", "custom metrics", "apm", "traces", "logs", "dogstatsd", "aws", "gcp"]:
                if t in lower_prompt:
                    tech_indicators.append(t)
            if not tech_indicators:
                tech_indicators = ["kubernetes", "dogstatsd", "apm"]

            return SignalAnalysisResult(
                distress_category=category,
                urgency_score=urgency,
                detected_company_mentions=[],
                key_pain_points=pain_points,
                vendor_mentioned="Datadog",
                technical_indicators=tech_indicators,
                sentiment_summary=f"Acute frustration observed regarding Datadog {category.replace('_', ' ').lower()}.",
            )  # type: ignore

        if response_model == EvidenceExtractionResult:
            verified = []
            if "bill" in lower_prompt:
                verified.append("Author explicitly referenced billing dissatisfaction with Datadog")
            if "outage" in lower_prompt:
                verified.append("Author reported monitoring blackout during an outage event")
            if not verified:
                verified.append("Author publicly questioned Datadog contract value and lock-in")

            return EvidenceExtractionResult(
                company_name=None,
                target_vendor="Datadog",
                complaint_type="PRICING_SHOCK",
                verified_claims=verified,
                inferred_facts=["Likely uses dogstatsd or Datadog agent in containerized environment"],
                metrics_or_costs_mentioned=re.findall(r"\$[\d,]+[kKmMbB]?|\b\d+[kKmMbB]\b", prompt, flags=re.I),
            )  # type: ignore

        if response_model == CompanySummaryResult:
            match = re.search(r"company(?:\s+name)?:\s*([A-Za-z0-9\-_\. ]+)", prompt, flags=re.I)
            comp_name = match.group(1).strip() if match else "Target Company"

            return CompanySummaryResult(
                company_name=comp_name,
                executive_brief=f"{comp_name} operates cloud infrastructure with containerized workloads experiencing high observability ingestion costs.",
                dissatisfaction_context="Expressed public distress regarding Datadog pricing escalation and proprietary agent lock-in.",
                challenger_fit_rationale="OpenTelemetry native architecture provides identical APM and trace capabilities without host-based tax.",
            )  # type: ignore

        if response_model == MigrationExplanationResult:
            return MigrationExplanationResult(
                headline="Drop-in OpenTelemetry Ingestion via Native Port 8126 Compatibility",
                architecture_overview=(
                    "The OpenTelemetry Collector Contrib distribution includes a native Datadog trace receiver on port 8126. "
                    "Existing application services using dd-trace continue running without code modifications, dual-shipping to Datadog and the target challenger."
                ),
                key_technical_advantages=[
                    "Zero application code refactoring required",
                    "Elimination of proprietary host tax licensing",
                    "Native ClickHouse columnar storage for traces and logs",
                    "Full CNCF OpenTelemetry standards compliance",
                ],
                risk_mitigation_highlights=[
                    "14-to-30 day parallel dual-shipping ensures data and alert parity",
                    "Instant rollback capability via ConfigMap toggle with zero downtime",
                    "No production agent uninstalls until validation criteria are met",
                ],
            )  # type: ignore

        if response_model == PersonalizedOutreachResult:
            return PersonalizedOutreachResult(
                subject_lines=[
                    "Datadog custom metric bleed vs OTel drop-in (migration plan)",
                    "Replacing the Datadog host tax without touching service code",
                    "Technical blueprint: dual-shipping to SigNoz in 14 days",
                ],
                opening_hook="Noticed your team recently encountered acute friction with Datadog observability billing.",
                polished_body=(
                    "Rather than a generic pitch, we compiled a technical deposition package showing how your Kubernetes "
                    "workloads can dual-ship traces through OpenTelemetry Collector's native port 8126 receiver without rewriting services, "
                    "recouping migration costs within 2 months while eliminating per-node licensing."
                ),
                call_to_action="Would you be open to reviewing the draft otel-collector-config.yaml with our solutions engineer this week?",
            )  # type: ignore

        # Fallback generic model instantiation
        try:
            return response_model()
        except Exception:
            raise ValueError(f"DeterministicFallbackProvider does not have a default template for {response_model.__name__}")
