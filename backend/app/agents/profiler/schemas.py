"""
Pydantic Schemas for the Profiler Agent.
Defines contracts for entity resolution, domain verification, technology profiling,
evidence validation, and ICP scoring.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    """Structured evidence finding with explicit anti-hallucination classification."""
    claim: str
    classification: str = Field(..., description="VERIFIED, INFERRED, UNKNOWN")
    source: str = Field(..., description="GitHub, DNS, JobPostings, PublicWeb, SignalContent")
    url: Optional[str] = None
    description: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DnsRecord(BaseModel):
    """Observed DNS record for a corporate domain."""
    record_type: str  # A, AAAA, MX, TXT, CNAME
    value: str
    source: str = "DNS"
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DnsVerificationResult(BaseModel):
    """Result of public DNS lookup on a company domain."""
    domain: str
    is_resolvable: bool = False
    records: List[DnsRecord] = Field(default_factory=list)
    mail_provider: Optional[str] = None
    cloud_or_cdn_provider: Optional[str] = None
    confidence: float = 0.0


class TechEvidence(BaseModel):
    """Concrete evidence of competitor or cloud technology usage."""
    technology: str
    category: str = "Observability"
    classification: str = "INFERRED"  # VERIFIED, INFERRED, UNKNOWN
    source: str  # GitHub, JobPostings, PublicWeb
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    snippet: Optional[str] = None
    confidence: float = 0.75
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TechStackProfileResult(BaseModel):
    """Comprehensive technology profile for an identified enterprise."""
    detected_technologies: Dict[str, List[str]] = Field(default_factory=dict)
    evidence: List[TechEvidence] = Field(default_factory=list)
    technology_confidence: float = 0.0
    has_datadog_evidence: bool = False
    has_k8s_evidence: bool = False
    has_otel_evidence: bool = False


class IcpDimensionScore(BaseModel):
    """Scoring breakdown for one dimension of the ICP model."""
    dimension: str
    weight: float
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    evidence: List[str] = Field(default_factory=list)


class IcpScoreReport(BaseModel):
    """Full explainable ICP assessment with separate score dimensions."""
    icp_fit_score: float = Field(ge=0.0, le=1.0)
    identity_confidence: float = Field(ge=0.0, le=1.0)
    technology_confidence: float = Field(ge=0.0, le=1.0)
    
    qualification_status: str = Field(..., description="ACCEPTED, REVIEW_REQUIRED, REJECTED")
    qualification_reason: str
    dimension_breakdown: Dict[str, IcpDimensionScore] = Field(default_factory=dict)


class EntityResolutionCandidate(BaseModel):
    """Identified company candidate resolved from a signal."""
    company_name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    estimated_size: str = "50-250 employees"
    identity_confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[EvidenceRecord] = Field(default_factory=list)
    decision_makers: List[Dict[str, Any]] = Field(default_factory=list)
    is_ambiguous: bool = False


class ProfilerExecutionSummary(BaseModel):
    """Report returned after running a profiling batch."""
    signals_processed: int = 0
    companies_identified: int = 0
    companies_accepted: int = 0
    companies_review_required: int = 0
    companies_rejected: int = 0
    unresolved_signals: int = 0
    errors: List[str] = Field(default_factory=list)
    execution_time_ms: int = 0


class ProfilerStatusReport(BaseModel):
    """Operational status of the Profiler Agent."""
    is_running: bool = False
    last_run_at: Optional[datetime] = None
    unprocessed_signals_count: int = 0
    total_companies_profiled: int = 0
    accepted_prospects_count: int = 0


class ProfilerMetricsReport(BaseModel):
    """Quantitative performance metrics for the Profiler Agent."""
    signals_processed: int = 0
    companies_identified: int = 0
    companies_accepted: int = 0
    companies_requiring_review: int = 0
    companies_rejected: int = 0
    unresolved_signals: int = 0
    average_icp_score: float = 0.0
    average_identity_confidence: float = 0.0
    average_technology_confidence: float = 0.0
