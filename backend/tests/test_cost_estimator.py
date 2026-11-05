"""
Tests for Cost Estimator.
"""

from app.agents.finops_architect.cost_estimator import CostEstimator


def test_derive_telemetry_inputs_from_signal_evidence():
    evidence = {"inferred_nodes": 200}
    inputs = CostEstimator.derive_telemetry_inputs(
        estimated_size="100-250 employees",
        infrastructure_indicators={},
        extracted_evidence=evidence,
    )
    input_map = {item.name: item.value for item in inputs}
    assert input_map["monitored_hosts"] == 200.0
    assert input_map["apm_hosts"] == 140.0  # 70% ratio
    assert input_map["custom_metrics"] == 20000.0
    for item in inputs:
        assert item.confidence > 0.0
        assert item.source != ""


def test_derive_telemetry_inputs_from_company_size_heuristic():
    inputs = CostEstimator.derive_telemetry_inputs(
        estimated_size="50-250 employees",
        infrastructure_indicators={},
        extracted_evidence={},
    )
    input_map = {item.name: item.value for item in inputs}
    assert input_map["monitored_hosts"] == 120.0
    assert input_map["apm_hosts"] == 84.0
