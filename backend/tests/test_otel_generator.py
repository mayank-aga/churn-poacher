"""
Tests for OpenTelemetry Collector YAML Generator.
"""

import yaml
from app.agents.finops_architect.otel_generator import OTelCollectorGenerator


def test_otel_collector_yaml_generation_and_validation():
    yaml_str = OTelCollectorGenerator.generate_collector_yaml(
        company_name="Acme Cloud",
        target_backend="SigNoz Cloud",
        enable_dual_shipping=True,
    )
    assert "Acme Cloud" in yaml_str
    assert "receivers" in yaml_str
    assert "exporters" in yaml_str

    # Validate syntax using pyyaml
    is_valid = OTelCollectorGenerator.validate_yaml(yaml_str)
    assert is_valid is True

    # Parse and inspect structure
    parsed = yaml.safe_load(yaml_str)
    assert "datadog" in parsed["receivers"]
    assert "otlp/signoz" in parsed["exporters"]
    assert "datadog" in parsed["exporters"]  # Dual shipping confirmed
    assert "traces" in parsed["service"]["pipelines"]


def test_yaml_validator_catches_invalid_content():
    invalid_yaml = "receivers: [unclosed bracket"
    assert OTelCollectorGenerator.validate_yaml(invalid_yaml) is False
