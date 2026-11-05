"""
Structured Output Schemas for LLM Intelligence Operations.
All LLM tasks validate against these Pydantic models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SignalAnalysisResult(BaseModel):
    """Result of LLM analysis of a public vendor complaint or status alert."""
    distress_category: str = Field(
        ...,
        description="Categorization: PRICING_SHOCK, OUTAGE_DOWNTIME, MIGRATION_INTENT, FEATURE_DEPRECATION, or GENERAL_DISCUSSION",
    )
    urgency_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Urgency from 0.0 (casual) to 1.0 (active production crisis or acute billing pain)",
    )
    detected_company_mentions: List[str] = Field(
        default_factory=list,
        description="Names of identifiable business entities mentioned in the text",
    )
    key_pain_points: List[str] = Field(
        default_factory=list,
        description="Bullet list of specific pain points expressed by the user",
    )
    vendor_mentioned: str = Field(
        default="Datadog",
        description="Incumbent vendor under discussion",
    )
    technical_indicators: List[str] = Field(
        default_factory=list,
        description="Keywords or technical technologies mentioned (e.g. Kubernetes, custom metrics, APM, traces, dogstatsd)",
    )
    sentiment_summary: str = Field(
        default="",
        description="One-sentence objective summary of the distress sentiment",
    )


class EvidenceExtractionResult(BaseModel):
    """Result of LLM evidence extraction from unstructured sources."""
    company_name: Optional[str] = None
    target_vendor: str = "Datadog"
    complaint_type: str = "PRICING_SHOCK"
    verified_claims: List[str] = Field(
        default_factory=list,
        description="Claims directly stated by the author with zero interpolation",
    )
    inferred_facts: List[str] = Field(
        default_factory=list,
        description="Reasonable inferences clearly tagged as inferred",
    )
    metrics_or_costs_mentioned: List[str] = Field(
        default_factory=list,
        description="Specific numerical costs or volume numbers stated in the source text",
    )


class CompanySummaryResult(BaseModel):
    """Executive summary of the prospect company and why they are vulnerable to migration."""
    company_name: str
    executive_brief: str = Field(
        ...,
        description="Two-sentence summary of the company's business model and engineering scale",
    )
    dissatisfaction_context: str = Field(
        ...,
        description="Summary of why this prospect is motivated to evaluate alternatives right now",
    )
    challenger_fit_rationale: str = Field(
        ...,
        description="Technical justification for why SigNoz or Grafana fits their requirements",
    )


class MigrationExplanationResult(BaseModel):
    """Natural language technical explanation of the OpenTelemetry migration."""
    headline: str = Field(
        ...,
        description="Attention-grabbing technical hook for an engineering decision maker",
    )
    architecture_overview: str = Field(
        ...,
        description="Concise description of the drop-in dual-shipping approach using port 8126",
    )
    key_technical_advantages: List[str] = Field(
        default_factory=list,
        description="3-4 concrete architectural benefits of migrating to open standards",
    )
    risk_mitigation_highlights: List[str] = Field(
        default_factory=list,
        description="Points addressing why this transition carries near-zero risk of downtime or data loss",
    )


class PersonalizedOutreachResult(BaseModel):
    """Polished sales outreach text tailored to the company's verified context."""
    subject_lines: List[str] = Field(
        default_factory=list,
        description="2-3 punchy, non-spammy subject lines",
    )
    opening_hook: str = Field(
        ...,
        description="High-empathy opening acknowledging the specific vendor pain without sounding creepy",
    )
    polished_body: str = Field(
        ...,
        description="Complete polished executive email body incorporating verified financial savings and migration steps",
    )
    call_to_action: str = Field(
        ...,
        description="Low-friction consultative CTA (e.g. offer to review collector config together)",
    )
