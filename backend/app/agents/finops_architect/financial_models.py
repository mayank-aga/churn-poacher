"""
Financial and Pricing Data Models for the FinOps Intelligence Agent.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class PricingEntry(BaseModel):
    """Configurable pricing unit for a monitoring vendor."""
    vendor: str  # Datadog, SigNoz Cloud, SigNoz Self-Hosted, Grafana Cloud, Grafana OSS
    product: str  # Infrastructure, APM, Custom Metrics, Logs, Traces
    billing_unit: str  # per_host_month, per_gb, per_100_metrics, per_million_spans
    unit_price: float
    currency: str = "USD"
    billing_period: str = "MONTHLY"
    pricing_source_url: str
    last_verified_date: str
    pricing_classification: str = "VERIFIED_PUBLIC"  # VERIFIED_PUBLIC, USER_PROVIDED, ESTIMATED, UNKNOWN


class InfrastructureInput(BaseModel):
    """Quantified infrastructure input used for expenditure estimation."""
    name: str
    value: float
    unit: str
    source: str  # ProfileInferred, UserProvided, SignalEvidence
    confidence: float = Field(ge=0.0, le=1.0)
    is_verified: bool = False


class PlatformCostBreakdown(BaseModel):
    """Line-item expenditure breakdown for a single platform."""
    platform_name: str
    infrastructure_hosts_cost: float = 0.0
    apm_cost: float = 0.0
    custom_metrics_cost: float = 0.0
    logs_cost: float = 0.0
    traces_cost: float = 0.0
    hosting_and_compute_cost: float = 0.0
    operational_maintenance_cost: float = 0.0
    total_monthly_cost: float = 0.0
    total_annual_cost: float = 0.0
    notes: List[str] = Field(default_factory=list)


class FinancialScenario(BaseModel):
    """Financial delta comparison under a specific telemetry volume scenario."""
    scenario_name: str  # LOW, BASE, HIGH
    assumptions_description: str
    
    current_datadog_monthly: float
    current_datadog_annual: float
    
    signoz_cloud_monthly: float
    signoz_cloud_annual: float
    signoz_cloud_annual_savings: float
    signoz_cloud_savings_pct: float
    
    signoz_self_hosted_monthly: float
    signoz_self_hosted_annual: float
    signoz_self_hosted_annual_savings: float
    
    grafana_cloud_monthly: float
    grafana_cloud_annual: float
    grafana_cloud_annual_savings: float
    
    grafana_oss_monthly: float
    grafana_oss_annual: float
    grafana_oss_annual_savings: float
    
    estimated_migration_cost: float
    payback_period_months: float
    three_year_tco_datadog: float
    three_year_tco_signoz_cloud: float
    three_year_tco_grafana_cloud: float


class SensitivityVariable(BaseModel):
    """Impact analysis of a variable on total monthly cost variance."""
    variable_name: str
    baseline_value: float
    tested_range: str
    monthly_impact_usd: float
    sensitivity_rank: int


class FinancialDeltaReport(BaseModel):
    """Complete Financial Delta Matrix produced by the FinOps Intelligence Agent."""
    company_id: str
    company_name: str
    target_challenger: str = "SigNoz"
    
    inputs_used: List[InfrastructureInput] = Field(default_factory=list)
    base_breakdown_datadog: PlatformCostBreakdown
    base_breakdown_signoz_cloud: PlatformCostBreakdown
    base_breakdown_grafana_cloud: PlatformCostBreakdown
    
    scenarios: Dict[str, FinancialScenario] = Field(default_factory=dict)
    sensitivity_analysis: List[SensitivityVariable] = Field(default_factory=list)
    confidence_score: float = Field(default=0.80, ge=0.0, le=1.0)
    data_sources: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)
