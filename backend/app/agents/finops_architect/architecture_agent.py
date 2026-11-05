"""
Architecture Migration Agent.
Orchestrates current architecture auditing, OpenTelemetry Collector configuration generation,
phased rollout planning, and rollback risk mitigation.
"""

from app.models.company import Company
from app.agents.finops_architect.architecture_models import ArchitectureMigrationBlueprint
from app.agents.finops_architect.architecture_analyzer import ArchitectureAnalyzer
from app.agents.finops_architect.otel_generator import OTelCollectorGenerator
from app.agents.finops_architect.migration_planner import MigrationPlanner
from app.agents.finops_architect.rollback_planner import RollbackPlanner


class ArchitectureAgent:
    @classmethod
    async def generate_migration_blueprint(
        cls,
        company: Company,
        target_backend: str = "SigNoz Cloud",
    ) -> ArchitectureMigrationBlueprint:
        """Produces a comprehensive technical architecture migration blueprint."""
        current_arch = ArchitectureAnalyzer.analyze_current_setup(company)
        collector_yaml = OTelCollectorGenerator.generate_collector_yaml(
            company_name=company.name,
            target_backend=target_backend,
            enable_dual_shipping=True,
        )
        phases = MigrationPlanner.generate_phased_plan(company.name, target_backend)
        rollback = RollbackPlanner.generate_rollback_strategy(company.name, target_backend)

        return ArchitectureMigrationBlueprint(
            company_id=company.id,
            company_name=company.name,
            target_backend=target_backend,
            current_architecture=current_arch,
            proposed_target_architecture=(
                f"Dual-shipping OpenTelemetry Collector deployment forwarding telemetry to {target_backend} "
                f"while maintaining parallel feeds to Datadog during the 14-day validation window."
            ),
            opentelemetry_strategy=(
                "Utilize the OpenTelemetry Collector's native Datadog receiver (:8126) to ingest traces from "
                "existing dd-trace application libraries without code changes, combined with standard OTLP "
                "exporters for modern cloud-native telemetry."
            ),
            collector_config_yaml=collector_yaml,
            dual_shipping_strategy="Simultaneous pipeline multiplexing via parallel exporter blocks in OTel Collector.",
            data_compatibility_matrix={
                "APM Tracing": "Full OpenTelemetry & Datadog trace format compatibility via OTel receiver-datadog.",
                "Custom Metrics": "dogstatsd gauges and counters mapped directly into OTel gauge/sum data points.",
                "Container Logs": "Standard JSON/container log format with resource attribute detection.",
            },
            phases=phases,
            rollback_plan=rollback,
            downtime_mitigation_and_risks=[
                {
                    "risk": "Telemetry ingestion lag during initial collector spin-up",
                    "mitigation": "Parallel deployment ensures original Datadog DaemonSet continues running uninterrupted.",
                },
                {
                    "risk": "Collector memory limits under sudden traffic bursts",
                    "mitigation": "memory_limiter processor configured at 75% hard limit with 20% spike threshold to prevent pod eviction.",
                },
            ],
            evidence_and_sources=[
                "https://opentelemetry.io/docs/collector/",
                "https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/datadogreceiver",
            ],
        )
