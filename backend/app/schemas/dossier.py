"""
Pydantic Schemas for Deposition Dossiers (Financial Delta Matrix, Migration Blueprint, Outreach Drafts).
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class CostScenario(BaseModel):
    low: float
    base: float
    high: float


class FinancialDeltaMatrix(BaseModel):
    vendor_current: str = "Datadog"
    target_challenger: str = "SigNoz"  # or Grafana
    
    # Cost estimates (Base scenario as primary, with low/high ranges)
    datadog_monthly: float
    datadog_annual: float
    datadog_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    signoz_monthly: float
    signoz_annual: float
    
    grafana_monthly: float
    grafana_annual: float
    
    estimated_migration_cost: float
    estimated_monthly_savings: float
    estimated_annual_savings: float
    payback_period_months: float
    
    scenarios: Dict[str, CostScenario] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.75, ge=0.0, le=1.0)
    data_sources: List[str] = Field(default_factory=list)


class MigrationPhase(BaseModel):
    phase_number: int
    name: str
    duration_days: int
    description: str
    rollback_trigger: str


class MigrationBlueprint(BaseModel):
    existing_architecture_assumptions: List[str] = Field(default_factory=list)
    proposed_architecture: str
    opentelemetry_strategy: str
    collector_config_yaml: str
    dual_shipping_strategy: str
    data_compatibility_matrix: Dict[str, str] = Field(default_factory=dict)
    phases: List[MigrationPhase] = Field(default_factory=list)
    rollback_strategy: str
    operational_risks_and_mitigations: List[Dict[str, str]] = Field(default_factory=list)


class OutreachDrafts(BaseModel):
    email_subject: str
    email_body: str
    linkedin_message: str
    technical_pitch: str
    financial_value_prop: str
    recommended_next_action: str
    approval_status: str = "DRAFT_PENDING_APPROVAL"  # DRAFT_PENDING_APPROVAL, APPROVED, REJECTED


class DossierBase(BaseModel):
    company_id: str
    signal_id: str
    financial_delta: Dict[str, Any] = Field(default_factory=dict)
    migration_blueprint: Dict[str, Any] = Field(default_factory=dict)
    outreach_drafts: Dict[str, Any] = Field(default_factory=dict)
    status: str = "DRAFT_PENDING_APPROVAL"
    is_synthetic: bool = False


class DossierCreate(DossierBase):
    pass


class DossierStatusUpdate(BaseModel):
    status: str = Field(..., description="DRAFT_PENDING_APPROVAL, APPROVED, REJECTED, SENT")


class DossierRead(DossierBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
