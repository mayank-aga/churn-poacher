"""
Value Proposition and Financial Case Generator for the Copywriter Agent.
Produces executive-ready 1-page business cases, TCO modeling, and the 'Datadog Tax' breakdown.
"""

from typing import Dict, Any
from app.agents.copywriter.schemas import ValuePropositionSummary


class ValuePropositionWriter:
    """Generates a structured financial business case and TCO comparison."""

    @classmethod
    def generate_value_proposition(
        cls,
        context: Dict[str, Any],
        finops_data: Dict[str, Any],
    ) -> ValuePropositionSummary:
        """Generates the 1-page financial business case."""
        company_name = context["company_name"]
        target_challenger = context["target_challenger"]

        base_scenario = finops_data.get("scenarios", {}).get("BASE") or finops_data.get("base_scenario") or {}
        datadog_annual = base_scenario.get("current_datadog_annual", 120000.0)
        target_annual = base_scenario.get("signoz_cloud_annual", 36000.0)
        annual_savings = base_scenario.get("signoz_cloud_annual_savings", 84000.0)
        savings_pct = base_scenario.get("signoz_cloud_savings_pct", 70.0)
        payback_months = base_scenario.get("payback_period_months", 1.8)
        migration_cost = base_scenario.get("estimated_migration_cost", 12600.0)
        three_year_datadog = base_scenario.get("three_year_tco_datadog", 360000.0)
        three_year_target = base_scenario.get("three_year_tco_signoz_cloud", 120600.0)
        three_year_net_savings = three_year_datadog - three_year_target

        savings_str = f"${annual_savings:,.0f}"
        datadog_str = f"${datadog_annual:,.0f}"
        target_str = f"${target_annual:,.0f}"
        three_year_str = f"${three_year_net_savings:,.0f}"

        tax_breakdown = {
            "Infrastructure Host Tax": "Datadog charges $15-$23/host/mo regardless of whether the host runs 1 container or 50. MicroVMs and auto-scaling clusters multiply this cost artificially.",
            "APM Host Penalty": "Additional $31-$40/host/mo for APM, even if only a fraction of services need distributed tracing on that node.",
            "Custom Metrics Overages": "$5 per 100 custom metrics per month with aggressive overage triggers on ephemeral pod tags.",
            "Log Re-indexing Surcharges": "Charges for log ingestion + separate retention index fees, creating steep price shocks during traffic spikes.",
        }

        risk_reward = [
            {
                "Dimension": "Financial Impact",
                "Status Quo (Datadog)": "Compounding run-rate scaling with node count; recurring overage penalties.",
                "Migration ({target_challenger})": f"Estimated ~{savings_str}/year reduction ({savings_pct:.0f}% savings); purely volume-based.",
            },
            {
                "Dimension": "Vendor Dependency",
                "Status Quo (Datadog)": "Proprietary agent lock-in and high switching barriers.",
                "Migration ({target_challenger})": "100% CNCF OpenTelemetry standard; portable across any OTLP backend.",
            },
            {
                "Dimension": "Operational Disruption",
                "Status Quo (Datadog)": "No migration effort, but recurring maintenance of overage caps.",
                "Migration ({target_challenger})": "Zero-code Datadog receiver (:8126); dual-shipping eliminates downtime risk.",
            },
        ]

        exec_summary = (
            f"Based on infrastructure modeling for {company_name}, migrating observability from Datadog to "
            f"{target_challenger} is projected to yield an estimated ~{savings_pct:.0f}% reduction in annual monitoring spend, "
            f"saving an estimated ~{savings_str} annually with a modeled payback period of ~{payback_months:.1f} months "
            f"and a 3-year net cumulative savings of ~{three_year_str}."
        )

        full_markdown = f"""# FinOps Business Case: Observability TCO Optimization
**Prepared for**: Financial and Engineering Leadership at {company_name}  
**Baseline Vendor**: Datadog | **Recommended Alternative**: {target_challenger}  
**Projected Annual Savings**: **~{savings_str}/year ({savings_pct:.0f}% reduction)**  
**Modeled Payback Horizon**: **~{payback_months:.1f} months** | **3-Year Cumulative Net Savings**: **~{three_year_str}**

---

## 1. Executive Summary
{exec_summary}

---

## 2. Comparative Expenditure Breakdown (Base Scenario)

| Cost Component | Current Datadog (Estimated) | Target {target_challenger} (Projected) | Annual Delta |
| :--- | :--- | :--- | :--- |
| **Annual Telemetry Spend** | {datadog_str}/yr | {target_str}/yr | -{savings_str}/yr |
| **Estimated Migration Cost** | $0 | ${migration_cost:,.0f} (one-time) | +${migration_cost:,.0f} |
| **Net Year 1 ROI** | Baseline | **{(annual_savings - migration_cost):,.0f} net savings** | **~{((annual_savings - migration_cost) / max(migration_cost, 1.0) * 100):.0f}% ROI** |
| **3-Year Cumulative TCO** | ${three_year_datadog:,.0f} | ${three_year_target:,.0f} | **-{three_year_str}** |

---

## 3. The 'Datadog Tax' Decomposition
Why does Datadog become unsustainable as engineering scale increases?
1. **Infrastructure Host Tax**: {tax_breakdown['Infrastructure Host Tax']}
2. **APM Host Penalty**: {tax_breakdown['APM Host Penalty']}
3. **Custom Metrics Multiplication**: {tax_breakdown['Custom Metrics Overages']}
4. **Log Retention Surcharges**: {tax_breakdown['Log Re-indexing Surcharges']}

---

## 4. Risk vs. Reward Decision Matrix

| Dimension | Datadog Status Quo | {target_challenger} Migration |
| :--- | :--- | :--- |
| **Financial Trajectory** | Increasing host tax & overage volatility | Pure volume-based, predictable unit economics |
| **Architectural Standard** | Closed-source proprietary lock-in | CNCF OpenTelemetry vendor neutrality |
| **Migration Risk** | Zero (no change) | Mitigated: Port 8126 zero-code receiver + dual-shipping |
| **Operational Control** | Black-box SaaS multi-tenant index | Direct columnar ClickHouse performance & data ownership |
"""

        return ValuePropositionSummary(
            executive_summary=exec_summary,
            current_estimated_runrate_annual=datadog_annual,
            target_alternative_runrate_annual=target_annual,
            annual_savings_usd=annual_savings,
            savings_percentage=savings_pct,
            datadog_tax_breakdown=tax_breakdown,
            tco_payback_period_months=payback_months,
            three_year_net_savings_usd=three_year_net_savings,
            risk_vs_reward=risk_reward,
            full_value_prop_markdown=full_markdown.strip(),
        )
