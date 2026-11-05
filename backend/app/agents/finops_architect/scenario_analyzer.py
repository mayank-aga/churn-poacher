"""
Scenario Analyzer & Sensitivity Model.
Computes low/base/high financial comparisons, payback periods, 3-year TCO,
and sensitivity impact analysis.
"""

from typing import Dict, List, Tuple
from app.agents.finops_architect.financial_models import (
    FinancialScenario,
    SensitivityVariable,
    InfrastructureInput,
)
from app.agents.finops_architect.pricing_engine import PricingEngine


class ScenarioAnalyzer:
    @classmethod
    def analyze_scenarios(
        cls,
        inputs: List[InfrastructureInput],
    ) -> Tuple[Dict[str, FinancialScenario], List[SensitivityVariable]]:
        """Generates LOW, BASE, HIGH scenarios and sensitivity variance rankings."""
        input_map = {item.name: item.value for item in inputs}
        base_hosts = input_map.get("monitored_hosts", 100.0)
        base_apm = input_map.get("apm_hosts", 70.0)
        base_metrics = input_map.get("custom_metrics", 10000.0)
        base_logs = input_map.get("monthly_log_gb", 2500.0)
        base_traces = input_map.get("monthly_trace_gb", 1500.0)

        # Multipliers for low and high scenarios
        scenario_configs = {
            "LOW": (0.65, "Conservative telemetry volume (-35% scale)"),
            "BASE": (1.00, "Expected baseline telemetry volume"),
            "HIGH": (1.50, "Heavy telemetry growth (+50% custom metrics and logs)"),
        }

        scenarios: Dict[str, FinancialScenario] = {}
        for sc_name, (mult, desc) in scenario_configs.items():
            h = base_hosts * mult
            apm = base_apm * mult
            metrics = base_metrics * mult
            logs = base_logs * mult
            traces = base_traces * mult

            dd = PricingEngine.calculate_datadog(h, apm, metrics, logs, traces)
            signoz_c = PricingEngine.calculate_signoz_cloud(h, apm, metrics, logs, traces)
            signoz_sh = PricingEngine.calculate_signoz_self_hosted(h, apm, metrics, logs, traces)
            grafana_c = PricingEngine.calculate_grafana_cloud(h, apm, metrics, logs, traces)
            grafana_oss = PricingEngine.calculate_grafana_oss(h, apm, metrics, logs, traces)

            # Monthly and Annual Savings vs SigNoz Cloud
            monthly_savings = max(0.0, dd.total_monthly_cost - signoz_c.total_monthly_cost)
            annual_savings = round(monthly_savings * 12.0, 2)
            savings_pct = round((annual_savings / dd.total_annual_cost * 100.0) if dd.total_annual_cost > 0 else 0.0, 1)

            # Migration cost estimate: ~80-120 engineering hours @ $125/hr
            migration_cost = round(12000.0 * mult, 2)
            payback_months = round((migration_cost / monthly_savings) if monthly_savings > 0 else 0.0, 1)

            # 3-Year Total Cost of Ownership (36 months + migration cost for challenger)
            tco_dd = round(dd.total_monthly_cost * 36.0, 2)
            tco_signoz = round((signoz_c.total_monthly_cost * 36.0) + migration_cost, 2)
            tco_grafana = round((grafana_c.total_monthly_cost * 36.0) + migration_cost, 2)

            scenarios[sc_name] = FinancialScenario(
                scenario_name=sc_name,
                assumptions_description=desc,
                current_datadog_monthly=dd.total_monthly_cost,
                current_datadog_annual=dd.total_annual_cost,
                signoz_cloud_monthly=signoz_c.total_monthly_cost,
                signoz_cloud_annual=signoz_c.total_annual_cost,
                signoz_cloud_annual_savings=annual_savings,
                signoz_cloud_savings_pct=savings_pct,
                signoz_self_hosted_monthly=signoz_sh.total_monthly_cost,
                signoz_self_hosted_annual=signoz_sh.total_annual_cost,
                signoz_self_hosted_annual_savings=round((dd.total_monthly_cost - signoz_sh.total_monthly_cost) * 12.0, 2),
                grafana_cloud_monthly=grafana_c.total_monthly_cost,
                grafana_cloud_annual=grafana_c.total_annual_cost,
                grafana_cloud_annual_savings=round((dd.total_monthly_cost - grafana_c.total_monthly_cost) * 12.0, 2),
                grafana_oss_monthly=grafana_oss.total_monthly_cost,
                grafana_oss_annual=grafana_oss.total_annual_cost,
                grafana_oss_annual_savings=round((dd.total_monthly_cost - grafana_oss.total_monthly_cost) * 12.0, 2),
                estimated_migration_cost=migration_cost,
                payback_period_months=payback_months,
                three_year_tco_datadog=tco_dd,
                three_year_tco_signoz_cloud=tco_signoz,
                three_year_tco_grafana_cloud=tco_grafana,
            )

        # Sensitivity Analysis: evaluate variance impact by perturbing single variables by +50%
        base_dd_cost = scenarios["BASE"].current_datadog_monthly
        
        # 1. Custom metrics +50%
        impact_metrics = PricingEngine.calculate_datadog(base_hosts, base_apm, base_metrics * 1.5, base_logs, base_traces).total_monthly_cost - base_dd_cost
        # 2. Host count +50%
        impact_hosts = PricingEngine.calculate_datadog(base_hosts * 1.5, base_apm * 1.5, base_metrics, base_logs, base_traces).total_monthly_cost - base_dd_cost
        # 3. Log volume +50%
        impact_logs = PricingEngine.calculate_datadog(base_hosts, base_apm, base_metrics, base_logs * 1.5, base_traces).total_monthly_cost - base_dd_cost

        sensitivity = [
            SensitivityVariable(
                variable_name="Host & APM Node Count",
                baseline_value=base_hosts,
                tested_range="+50% expansion",
                monthly_impact_usd=round(impact_hosts, 2),
                sensitivity_rank=1 if impact_hosts >= max(impact_metrics, impact_logs) else 2,
            ),
            SensitivityVariable(
                variable_name="Custom Metrics Series",
                baseline_value=base_metrics,
                tested_range="+50% metric series",
                monthly_impact_usd=round(impact_metrics, 2),
                sensitivity_rank=1 if impact_metrics >= max(impact_hosts, impact_logs) else 2,
            ),
            SensitivityVariable(
                variable_name="Log Ingestion Volume",
                baseline_value=base_logs,
                tested_range="+50% GB ingested",
                monthly_impact_usd=round(impact_logs, 2),
                sensitivity_rank=3,
            ),
        ]
        sensitivity.sort(key=lambda s: s.monthly_impact_usd, reverse=True)
        for idx, item in enumerate(sensitivity):
            item.sensitivity_rank = idx + 1

        return scenarios, sensitivity
