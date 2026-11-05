"""
Architecture and Migration Data Models for the Architecture Migration Agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ArchitectureComponent(BaseModel):
    name: str
    category: str  # Ingestion, Agent, Processor, Storage, UI
    classification: str = "INFERRED"  # VERIFIED, INFERRED, UNKNOWN
    details: str


class CurrentArchitectureAssessment(BaseModel):
    """Structured assessment of the enterprise's current telemetry setup."""
    application_services: List[ArchitectureComponent] = Field(default_factory=list)
    kubernetes_environments: List[str] = Field(default_factory=list)
    datadog_agents_detected: bool = True
    apm_instrumentation: str = "Datadog dd-trace library / agent"
    log_collection_method: str = "Datadog DaemonSet / filelog"
    metrics_collection_method: str = "dogstatsd UDP + Prometheus scrape"
    trace_collection_method: str = "Datadog Trace Agent :8126"


class MigrationPhase(BaseModel):
    """Detailed tasks and milestones for one phase of the migration."""
    phase_number: int
    name: str
    duration_days: int
    tasks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    potential_risks: List[str] = Field(default_factory=list)
    rollback_triggers: List[str] = Field(default_factory=list)


class RollbackPlan(BaseModel):
    """Concrete operational rollback procedures to prevent data loss or downtime."""
    revert_steps: List[str] = Field(default_factory=list)
    data_preservation_strategy: str
    monitoring_and_parity_checks: List[str] = Field(default_factory=list)
    irreversible_actions_warning: List[str] = Field(default_factory=list)


class ArchitectureMigrationBlueprint(BaseModel):
    """Complete migration architecture specification produced by the Architecture Agent."""
    company_id: str
    company_name: str
    target_backend: str = "SigNoz Cloud (OpenTelemetry native)"
    
    current_architecture: CurrentArchitectureAssessment
    proposed_target_architecture: str
    opentelemetry_strategy: str
    collector_config_yaml: str
    dual_shipping_strategy: str
    data_compatibility_matrix: Dict[str, str] = Field(default_factory=dict)
    phases: List[MigrationPhase] = Field(default_factory=list)
    rollback_plan: RollbackPlan
    downtime_mitigation_and_risks: List[Dict[str, str]] = Field(default_factory=list)
    evidence_and_sources: List[str] = Field(default_factory=list)
