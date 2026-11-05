"""
Tests for Pricing Engine across all five platforms.
"""

from app.agents.finops_architect.pricing_engine import PricingEngine
from app.agents.finops_architect.pricing_sources import PricingCatalog


def test_pricing_catalog_integrity():
    entries = PricingCatalog.get_all_entries()
    assert len(entries) >= 10
    for e in entries:
        assert e.unit_price >= 0.0
        assert e.currency == "USD"
        assert e.pricing_source_url.startswith("https://")
        assert e.pricing_classification in ["VERIFIED_PUBLIC", "ESTIMATED"]


def test_pricing_engine_datadog_calculation():
    # 100 hosts, 70 APM hosts, 10,000 custom metrics, 2500 GB logs, 1500 GB traces
    breakdown = PricingEngine.calculate_datadog(
        hosts=100.0,
        apm_hosts=70.0,
        custom_metrics=10000.0,
        log_gb=2500.0,
        trace_gb=1500.0,
    )
    assert breakdown.platform_name == "Datadog"
    assert breakdown.infrastructure_hosts_cost == 100.0 * 23.00  # $2,300
    assert breakdown.apm_cost == 70.0 * 31.00  # $2,170
    assert breakdown.custom_metrics_cost == (10000.0 / 100.0) * 5.00  # $500
    assert breakdown.total_monthly_cost > 7000.0
    assert breakdown.total_annual_cost == round(breakdown.total_monthly_cost * 12.0, 2)


def test_pricing_engine_signoz_cloud_zero_host_tax():
    # SigNoz Cloud must have $0 host cost and $0 APM license fee
    breakdown = PricingEngine.calculate_signoz_cloud(
        hosts=100.0,
        apm_hosts=70.0,
        custom_metrics=10000.0,
        log_gb=2500.0,
        trace_gb=1500.0,
    )
    assert breakdown.platform_name == "SigNoz Cloud"
    assert breakdown.infrastructure_hosts_cost == 0.0
    assert breakdown.apm_cost == 0.0
    assert breakdown.total_monthly_cost < 1000.0  # Significant savings over Datadog


def test_pricing_engine_grafana_cloud():
    breakdown = PricingEngine.calculate_grafana_cloud(
        hosts=100.0,
        apm_hosts=70.0,
        custom_metrics=10000.0,
        log_gb=2500.0,
        trace_gb=1500.0,
    )
    assert breakdown.platform_name == "Grafana Cloud"
    assert breakdown.total_monthly_cost > 0.0
