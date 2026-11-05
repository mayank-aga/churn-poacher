"""
FinOps Intelligence Agent.
Orchestrates infrastructure cost estimation, competitive pricing calculations,
scenario modeling, and Financial Delta Matrix synthesis.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company
from app.models.signal import Signal
from app.agents.finops_architect.financial_models import FinancialDeltaReport
from app.agents.finops_architect.cost_estimator import CostEstimator
from app.agents.finops_architect.pricing_engine import PricingEngine
from app.agents.finops_architect.scenario_analyzer import ScenarioAnalyzer


class FinOpsAgent:
    """Calculates granular, transparent financial comparisons against Datadog."""

    @classmethod
    async def generate_financial_analysis(
        cls,
        company: Company,
        signal: Optional[Signal] = None,
    ) -> FinancialDeltaReport:
        """Produces a complete Financial Delta Report with low/base/high scenarios."""
        # 1. Derive Telemetry Inputs
        inputs = CostEstimator.derive_telemetry_inputs(
            estimated_size=company.estimated_size,
            infrastructure_indicators=company.infrastructure_indicators or {},
            extracted_evidence=signal.extracted_evidence if signal else {},
        )
        input_map = {item.name: item.value for item in inputs}
        hosts = input_map["monitored_hosts"]
        apm = input_map["apm_hosts"]
        metrics = input_map["custom_metrics"]
        logs = input_map["monthly_log_gb"]
        traces = input_map["monthly_trace_gb"]

        # 2. Base Platform Breakdowns
        dd_base = PricingEngine.calculate_datadog(hosts, apm, metrics, logs, traces)
        signoz_base = PricingEngine.calculate_signoz_cloud(hosts, apm, metrics, logs, traces)
        grafana_base = PricingEngine.calculate_grafana_cloud(hosts, apm, metrics, logs, traces)

        # 3. Scenario & Sensitivity Analysis
        scenarios, sensitivity = ScenarioAnalyzer.analyze_scenarios(inputs)

        # 4. Compile Structured Report
        return FinancialDeltaReport(
            company_id=company.id,
            company_name=company.name,
            target_challenger="SigNoz",
            inputs_used=inputs,
            base_breakdown_datadog=dd_base,
            base_breakdown_signoz_cloud=signoz_base,
            base_breakdown_grafana_cloud=grafana_base,
            scenarios=scenarios,
            sensitivity_analysis=sensitivity,
            confidence_score=0.82,
            data_sources=[
                "https://www.datadoghq.com/pricing/",
                "https://signoz.io/pricing/",
                "https://grafana.com/pricing/",
            ],
            caveats=[
                "Estimates assume standard public published list pricing; does not reflect undisclosed enterprise volume discounts.",
                "Actual customer network egress and custom retention tiers may alter absolute figures.",
            ]
        )
