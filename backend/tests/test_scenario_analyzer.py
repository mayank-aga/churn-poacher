"""
Tests for Scenario Analyzer and Sensitivity Analysis.
"""

from app.agents.finops_architect.cost_estimator import CostEstimator
from app.agents.finops_architect.scenario_analyzer import ScenarioAnalyzer


def test_scenario_analysis_low_base_high():
    inputs = CostEstimator.derive_telemetry_inputs(
        estimated_size="100-250 employees",
        infrastructure_indicators={},
        extracted_evidence={"inferred_nodes": 150},
    )
    scenarios, sensitivity = ScenarioAnalyzer.analyze_scenarios(inputs)

    assert "LOW" in scenarios
    assert "BASE" in scenarios
    assert "HIGH" in scenarios

    base = scenarios["BASE"]
    low = scenarios["LOW"]
    high = scenarios["HIGH"]

    # Monotonic scaling check
    assert low.current_datadog_monthly < base.current_datadog_monthly < high.current_datadog_monthly
    assert base.signoz_cloud_annual_savings > 0.0
    assert base.payback_period_months > 0.0
    assert base.three_year_tco_datadog > base.three_year_tco_signoz_cloud


def test_sensitivity_ranking():
    inputs = CostEstimator.derive_telemetry_inputs(
        estimated_size="100-250 employees",
        infrastructure_indicators={},
        extracted_evidence={"inferred_nodes": 150},
    )
    _, sensitivity = ScenarioAnalyzer.analyze_scenarios(inputs)

    assert len(sensitivity) == 3
    # Check that rank 1 has the largest monthly USD impact
    assert sensitivity[0].monthly_impact_usd >= sensitivity[1].monthly_impact_usd
    assert sensitivity[0].sensitivity_rank == 1
