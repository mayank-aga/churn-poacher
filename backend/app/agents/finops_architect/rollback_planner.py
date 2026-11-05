"""
Rollback Planner.
Provides actionable operational rollback procedures ensuring zero data loss and risk-free migration.
"""

from app.agents.finops_architect.architecture_models import RollbackPlan


class RollbackPlanner:
    @classmethod
    def generate_rollback_strategy(
        cls,
        company_name: str,
        target_backend: str = "SigNoz Cloud",
    ) -> RollbackPlan:
        """Constructs an executable rollback playbook for DevOps and SRE leads."""
        return RollbackPlan(
            revert_steps=[
                "1. Keep existing Datadog DaemonSet active in parallel during Phases 2 through 5.",
                "2. If an anomaly is detected in the challenger backend, toggle OTel Collector exporter: remove 'otlp/signoz' from service pipeline and keep 'datadog'.",
                "3. Revert app container DNS/env variable `DD_AGENT_HOST` back to the standard Datadog DaemonSet host IP via Helm/Kustomize rollback.",
                "4. Restart application pods in rolling waves with zero downtime.",
                "5. Verify Datadog Live Container and APM streams resume full fidelity within 60 seconds.",
            ],
            data_preservation_strategy=(
                "Dual-shipping writes identical trace IDs, log entries, and gauge values to both Datadog "
                "and the challenger simultaneously. Rolling back does not cause historical metric gaps because "
                "Datadog was never disconnected during the validation window."
            ),
            monitoring_and_parity_checks=[
                "Compare 5-minute metric rollups between Datadog Metrics Explorer and SigNoz / Grafana.",
                "Verify span duration percentiles (p50, p95, p99) match across distributed trace views.",
                "Validate critical P1 monitor alert thresholds trigger identically in staging tests.",
            ],
            irreversible_actions_warning=[
                "DO NOT delete the Datadog API key or terminate the annual contract until Phase 6 is fully concluded.",
                "DO NOT uninstall Datadog DaemonSets prior to Phase 7 sign-off by VP of Engineering.",
            ],
        )
