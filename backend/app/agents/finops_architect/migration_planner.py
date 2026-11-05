"""
Phased Migration Planner.
Generates a structured 7-phase takeout roadmap from Datadog to SigNoz or Grafana Cloud.
"""

from typing import List
from app.agents.finops_architect.architecture_models import MigrationPhase


class MigrationPlanner:
    @classmethod
    def generate_phased_plan(
        cls,
        company_name: str,
        target_backend: str = "SigNoz Cloud",
    ) -> List[MigrationPhase]:
        """Produces a 7-stage zero-loss migration plan."""
        return [
            MigrationPhase(
                phase_number=1,
                name="Telemetry Discovery & Footprint Audit",
                duration_days=3,
                tasks=[
                    "Audit existing Datadog agent daemonsets and host configurations.",
                    "Catalog custom metric namespaces, tag volumes, and high-cardinality series.",
                    "Enumerate active APM services instrumented with dd-trace.",
                ],
                dependencies=["Access to staging and read-only production environment"],
                success_criteria=[
                    "Complete inventory of all telemetry inputs and custom metric tags.",
                ],
                potential_risks=["Undocumented custom metric generators or legacy sidecars"],
                rollback_triggers=["Discovery reveals proprietary proprietary integrations without OTel translation"],
            ),
            MigrationPhase(
                phase_number=2,
                name="Parallel OpenTelemetry Collector Deployment",
                duration_days=4,
                tasks=[
                    f"Deploy OTel Collector DaemonSet/Deployment in parallel alongside Datadog agent.",
                    "Configure Datadog compatibility receiver (:8126) and OTLP ports (:4317/:4318).",
                    "Establish TLS egress credentials to target challenger backend.",
                ],
                dependencies=["Phase 1 completion"],
                success_criteria=[
                    "OTel Collector pods healthy with memory_limiter extension passing healthchecks.",
                ],
                potential_risks=["Resource contention on smaller worker nodes"],
                rollback_triggers=["Collector OOM kills or CPU throttle above 15% threshold"],
            ),
            MigrationPhase(
                phase_number=3,
                name="Dual-Shipping & Data Parity Validation",
                duration_days=7,
                tasks=[
                    "Enable dual-shipping exporter in OTel Collector (routing simultaneously to Datadog and SigNoz/Grafana).",
                    "Re-route 10% canary service traffic through local collector.",
                    "Run automated trace and span count comparison queries across both platforms.",
                ],
                dependencies=["Phase 2 deployment verified"],
                success_criteria=[
                    "Metric and span count parity within 99.5% accuracy between Datadog and challenger backend.",
                ],
                potential_risks=["Network egress double-bandwidth during verification window"],
                rollback_triggers=["Trace loss exceeding 0.5% or latency degradation on canary workloads"],
            ),
            MigrationPhase(
                phase_number=4,
                name="Performance & Dashboard Cost Verification",
                duration_days=7,
                tasks=[
                    "Replicate top critical production alerting rules and SLAs in new backend.",
                    "Verify query response latency on high-cardinality dashboards.",
                    "Review 7-day usage invoice on challenger to confirm financial delta projection.",
                ],
                dependencies=["Phase 3 parity confirmed"],
                success_criteria=[
                    "Dashboard load times <= 1.2s; verified spend reduction >= 60% vs Datadog rate.",
                ],
                potential_risks=["Missing complex custom alerting formulas"],
                rollback_triggers=["Inability to replicate P1 SLA monitors or unexpected consumption surge"],
            ),
            MigrationPhase(
                phase_number=5,
                name="Gradual Traffic Cutover (Canary Waves)",
                duration_days=9,
                tasks=[
                    "Shift 25% -> 50% -> 100% of production service telemetry through OTel Collector.",
                    "Keep Datadog dual-shipping active in background as a warm standby safety net.",
                ],
                dependencies=["Phase 4 sign-off by SRE & DevOps leads"],
                success_criteria=[
                    "100% of telemetry processed via OTel Collector with zero dropped packets.",
                ],
                potential_risks=["Spike in network socket buffer usage during peak load"],
                rollback_triggers=["Any critical alerting failure during production peak windows"],
            ),
            MigrationPhase(
                phase_number=6,
                name="Datadog Dependency Reduction",
                duration_days=15,
                tasks=[
                    "Disable Datadog dual-shipping exporter in Collector config.",
                    "Archive historical Datadog dashboards and exported telemetry.",
                ],
                dependencies=["Phase 5 stable for 14 continuous days without incidents"],
                success_criteria=[
                    "Datadog daily ingestion drops to 0 GB; new backend serves 100% of SRE queries.",
                ],
                potential_risks=["Forgotten background cron jobs still pointing to Datadog agent"],
                rollback_triggers=["Re-enable Datadog exporter via 1-line collector config change if needed"],
            ),
            MigrationPhase(
                phase_number=7,
                name="Final Decommissioning & Contract Termination",
                duration_days=15,
                tasks=[
                    "Decommission legacy Datadog agent DaemonSets from clusters.",
                    "Submit formal cancellation / renewal deprecation notice to Datadog sales.",
                ],
                dependencies=["Phase 6 completed and approved by VP of Engineering"],
                success_criteria=[
                    "Cluster resources reclaimed (~150MB RAM/node); recurring Datadog bill eliminated.",
                ],
                potential_risks=["Contract early termination dispute"],
                rollback_triggers=["None (Final milestone)"],
            ),
        ]
