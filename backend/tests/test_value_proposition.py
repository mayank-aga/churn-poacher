"""
Tests for Value Proposition and Business Case Generator.
Verifies financial accuracy, TCO calculations, and the 'Datadog Tax' decomposition.
"""

import pytest
from app.agents.copywriter.value_proposition import ValuePropositionWriter
from app.agents.copywriter.personalization import PersonalizationEngine


def test_value_proposition_financial_integrity():
    company_data = {
        "name": "FinTech Matrix",
        "domain": "fintechmatrix.com",
        "industry": "Financial Services",
        "estimated_size": "250-1000 employees",
    }
    signal_data = {
        "complaint_category": "BILLING_SHOCK",
    }
    finops_data = {
        "scenarios": {
            "BASE": {
                "current_datadog_annual": 240000.0,
                "signoz_cloud_annual": 72000.0,
                "signoz_cloud_annual_savings": 168000.0,
                "signoz_cloud_savings_pct": 70.0,
                "payback_period_months": 1.4,
                "estimated_migration_cost": 15000.0,
                "three_year_tco_datadog": 720000.0,
                "three_year_tco_signoz_cloud": 231000.0,
            }
        }
    }

    context = PersonalizationEngine.get_context(company_data, signal_data, "SigNoz Cloud")
    val_prop = ValuePropositionWriter.generate_value_proposition(context, finops_data)

    assert val_prop.current_estimated_runrate_annual == 240000.0
    assert val_prop.target_alternative_runrate_annual == 72000.0
    assert val_prop.annual_savings_usd == 168000.0
    assert val_prop.savings_percentage == 70.0
    assert val_prop.tco_payback_period_months == 1.4
    assert val_prop.three_year_net_savings_usd == (720000.0 - 231000.0)

    # Datadog Tax breakdown assertions
    assert "Host Tax" in str(val_prop.datadog_tax_breakdown)
    assert "Custom Metrics" in str(val_prop.datadog_tax_breakdown)

    # Markdown output checks
    assert "$168,000" in val_prop.full_value_prop_markdown
    assert "Risk vs. Reward" in val_prop.full_value_prop_markdown
    assert "Payback" in val_prop.full_value_prop_markdown
