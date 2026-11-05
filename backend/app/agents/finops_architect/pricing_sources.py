"""
Official Pricing Sources and Reference Catalog for Supported Platforms.
All prices are tracked with official source URLs, verification dates, and classifications.
"""

from typing import Dict, List
from app.agents.finops_architect.financial_models import PricingEntry


class PricingCatalog:
    """Maintains verified, publicly published unit prices for monitoring vendors."""

    CATALOG: Dict[str, List[PricingEntry]] = {
        "Datadog": [
            PricingEntry(
                vendor="Datadog",
                product="Infrastructure Pro",
                billing_unit="per_host_month",
                unit_price=15.00,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Datadog",
                product="Infrastructure Enterprise",
                billing_unit="per_host_month",
                unit_price=23.00,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Datadog",
                product="APM & Continuous Profiler",
                billing_unit="per_host_month",
                unit_price=31.00,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Datadog",
                product="Custom Metrics",
                billing_unit="per_100_metrics_month",
                unit_price=5.00,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Datadog",
                product="Log Ingestion",
                billing_unit="per_gb",
                unit_price=0.10,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Datadog",
                product="Log Retention (15 days)",
                billing_unit="per_million_events",
                unit_price=1.70,
                pricing_source_url="https://www.datadoghq.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
        ],
        "SigNoz Cloud": [
            PricingEntry(
                vendor="SigNoz Cloud",
                product="Logs Ingestion & Retention (15d included)",
                billing_unit="per_gb",
                unit_price=0.10,
                pricing_source_url="https://signoz.io/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="SigNoz Cloud",
                product="Traces Ingestion",
                billing_unit="per_gb",
                unit_price=0.10,
                pricing_source_url="https://signoz.io/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="SigNoz Cloud",
                product="Metrics Ingestion",
                billing_unit="per_million_samples",
                unit_price=0.10,
                pricing_source_url="https://signoz.io/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="SigNoz Cloud",
                product="Host License",
                billing_unit="per_host_month",
                unit_price=0.00,  # Zero per-node tax
                pricing_source_url="https://signoz.io/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
        ],
        "SigNoz Self-Hosted": [
            PricingEntry(
                vendor="SigNoz Self-Hosted",
                product="Community Edition Software",
                billing_unit="software_license",
                unit_price=0.00,
                pricing_source_url="https://github.com/SigNoz/signoz",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="SigNoz Self-Hosted",
                product="Estimated Cloud Infrastructure (AWS ClickHouse & Nodes)",
                billing_unit="per_month_cluster",
                unit_price=350.00,
                pricing_source_url="https://aws.amazon.com/ec2/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="ESTIMATED",
            ),
        ],
        "Grafana Cloud": [
            PricingEntry(
                vendor="Grafana Cloud",
                product="Metrics",
                billing_unit="per_1000_active_series",
                unit_price=8.00,
                pricing_source_url="https://grafana.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Grafana Cloud",
                product="Logs (30d retention included)",
                billing_unit="per_gb",
                unit_price=0.50,
                pricing_source_url="https://grafana.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Grafana Cloud",
                product="Traces",
                billing_unit="per_gb",
                unit_price=0.50,
                pricing_source_url="https://grafana.com/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
        ],
        "Grafana OSS": [
            PricingEntry(
                vendor="Grafana OSS",
                product="Mimir/Loki/Tempo Software",
                billing_unit="software_license",
                unit_price=0.00,
                pricing_source_url="https://grafana.com/oss/",
                last_verified_date="2026-10-15",
                pricing_classification="VERIFIED_PUBLIC",
            ),
            PricingEntry(
                vendor="Grafana OSS",
                product="Estimated Cloud Storage & Compute",
                billing_unit="per_month_cluster",
                unit_price=450.00,
                pricing_source_url="https://aws.amazon.com/ec2/pricing/",
                last_verified_date="2026-10-15",
                pricing_classification="ESTIMATED",
            ),
        ],
    }

    @classmethod
    def get_all_entries(cls) -> List[PricingEntry]:
        all_entries = []
        for entries in cls.CATALOG.values():
            all_entries.extend(entries)
        return all_entries

    @classmethod
    def get_vendor_entries(cls, vendor: str) -> List[PricingEntry]:
        return cls.CATALOG.get(vendor, [])
