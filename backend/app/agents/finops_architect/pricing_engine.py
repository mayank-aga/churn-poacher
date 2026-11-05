"""
Pricing Engine.
Computes itemized platform expenditure across all five supported monitoring platforms.
"""

from app.agents.finops_architect.financial_models import PlatformCostBreakdown
from app.agents.finops_architect.pricing_sources import PricingCatalog


class PricingEngine:
    @classmethod
    def calculate_datadog(
        cls,
        hosts: float,
        apm_hosts: float,
        custom_metrics: float,
        log_gb: float,
        trace_gb: float,
    ) -> PlatformCostBreakdown:
        """Calculates Datadog expenditure using official enterprise tier published pricing."""
        # Infrastructure Pro ($15) or Enterprise ($23). Defaulting to Enterprise for Kubernetes/Containers
        host_cost = hosts * 23.00
        apm_cost = apm_hosts * 31.00
        # Custom Metrics: $5.00 per 100 metrics
        custom_metrics_cost = (custom_metrics / 100.0) * 5.00
        # Logs: $0.10/GB ingestion + $1.70 per million retained events (~1.5GB/million events = ~$1.06/GB)
        logs_cost = (log_gb * 0.10) + (log_gb * 1.06)
        # APM Trace ingestion: $0.10/GB
        traces_cost = trace_gb * 0.10

        total_monthly = round(host_cost + apm_cost + custom_metrics_cost + logs_cost + traces_cost, 2)
        total_annual = round(total_monthly * 12.0, 2)

        return PlatformCostBreakdown(
            platform_name="Datadog",
            infrastructure_hosts_cost=round(host_cost, 2),
            apm_cost=round(apm_cost, 2),
            custom_metrics_cost=round(custom_metrics_cost, 2),
            logs_cost=round(logs_cost, 2),
            traces_cost=round(traces_cost, 2),
            total_monthly_cost=total_monthly,
            total_annual_cost=total_annual,
            notes=[
                "Assumes Enterprise host pricing ($23/host) + APM & Profiler ($31/host).",
                "Custom metrics billed at standard $5.00 per 100 metrics block.",
                "Logs calculated at $0.10/GB ingest + 15-day indexed retention ($1.06/GB equivalent).",
            ]
        )

    @classmethod
    def calculate_signoz_cloud(
        cls,
        hosts: float,
        apm_hosts: float,
        custom_metrics: float,
        log_gb: float,
        trace_gb: float,
    ) -> PlatformCostBreakdown:
        """Calculates SigNoz Cloud expenditure (no per-host fee, usage-based ingestion only)."""
        # Host & APM license: $0 (SigNoz does not charge a per-host tax)
        host_cost = 0.0
        apm_cost = 0.0
        # Logs & Traces: $0.10/GB (includes 15 days retention free)
        logs_cost = log_gb * 0.10
        traces_cost = trace_gb * 0.10
        # Metrics: $0.10 per million samples (~100 metrics with 15s scrape = ~17M samples/mo = ~$1.70 vs DD $5.00)
        custom_metrics_cost = (custom_metrics / 100.0) * 1.70

        total_monthly = round(host_cost + apm_cost + custom_metrics_cost + logs_cost + traces_cost, 2)
        total_annual = round(total_monthly * 12.0, 2)

        return PlatformCostBreakdown(
            platform_name="SigNoz Cloud",
            infrastructure_hosts_cost=0.0,
            apm_cost=0.0,
            custom_metrics_cost=round(custom_metrics_cost, 2),
            logs_cost=round(logs_cost, 2),
            traces_cost=round(traces_cost, 2),
            total_monthly_cost=total_monthly,
            total_annual_cost=total_annual,
            notes=[
                "Zero per-host or per-APM license fees (pure consumption pricing).",
                "Includes 15-day log and trace retention without retention surcharge.",
            ]
        )

    @classmethod
    def calculate_signoz_self_hosted(
        cls,
        hosts: float,
        apm_hosts: float,
        custom_metrics: float,
        log_gb: float,
        trace_gb: float,
    ) -> PlatformCostBreakdown:
        """Calculates SigNoz Self-Hosted expenditure (software free, compute/storage infrastructure)."""
        # Baseline compute: ClickHouse multi-AZ instance scaled to volume
        base_infra = 350.00
        storage_cost = (log_gb + trace_gb) * 0.04  # S3/EBS storage cost at compressed rates
        hosting = base_infra + storage_cost
        maintenance = 200.00  # Approx 2 hours SRE time per month

        total_monthly = round(hosting + maintenance, 2)
        total_annual = round(total_monthly * 12.0, 2)

        return PlatformCostBreakdown(
            platform_name="SigNoz Self-Hosted",
            infrastructure_hosts_cost=0.0,
            apm_cost=0.0,
            custom_metrics_cost=0.0,
            logs_cost=0.0,
            traces_cost=0.0,
            hosting_and_compute_cost=round(hosting, 2),
            operational_maintenance_cost=maintenance,
            total_monthly_cost=total_monthly,
            total_annual_cost=total_annual,
            notes=[
                "Software license is 100% Free Open Source (Apache 2.0).",
                "Includes estimated AWS ClickHouse cluster compute, EBS/S3 storage, and SRE maintenance hours.",
            ]
        )

    @classmethod
    def calculate_grafana_cloud(
        cls,
        hosts: float,
        apm_hosts: float,
        custom_metrics: float,
        log_gb: float,
        trace_gb: float,
    ) -> PlatformCostBreakdown:
        """Calculates Grafana Cloud expenditure."""
        # Active series: ~$8.00 per 1000 series
        active_series = custom_metrics * 1.5
        metrics_cost = (active_series / 1000.0) * 8.00
        # Logs & Traces: $0.50/GB (includes 30 days retention)
        logs_cost = log_gb * 0.50
        traces_cost = trace_gb * 0.50

        total_monthly = round(metrics_cost + logs_cost + traces_cost, 2)
        total_annual = round(total_monthly * 12.0, 2)

        return PlatformCostBreakdown(
            platform_name="Grafana Cloud",
            infrastructure_hosts_cost=0.0,
            apm_cost=0.0,
            custom_metrics_cost=round(metrics_cost, 2),
            logs_cost=round(logs_cost, 2),
            traces_cost=round(traces_cost, 2),
            total_monthly_cost=total_monthly,
            total_annual_cost=total_annual,
            notes=[
                "Billed at published Grafana Cloud rates: $8.00/1k series, $0.50/GB logs & traces.",
                "Includes 30 days retention out-of-the-box.",
            ]
        )

    @classmethod
    def calculate_grafana_oss(
        cls,
        hosts: float,
        apm_hosts: float,
        custom_metrics: float,
        log_gb: float,
        trace_gb: float,
    ) -> PlatformCostBreakdown:
        """Calculates self-hosted Grafana Mimir + Loki + Tempo stack."""
        base_infra = 450.00
        storage_cost = (log_gb + trace_gb) * 0.05
        hosting = base_infra + storage_cost
        maintenance = 300.00  # Multi-component OSS maintenance

        total_monthly = round(hosting + maintenance, 2)
        total_annual = round(total_monthly * 12.0, 2)

        return PlatformCostBreakdown(
            platform_name="Grafana OSS",
            hosting_and_compute_cost=round(hosting, 2),
            operational_maintenance_cost=maintenance,
            total_monthly_cost=total_monthly,
            total_annual_cost=total_annual,
            notes=[
                "Self-hosted Mimir (Metrics), Loki (Logs), Tempo (Traces), Grafana UI.",
                "Includes estimated multi-node Kubernetes compute and storage.",
            ]
        )
