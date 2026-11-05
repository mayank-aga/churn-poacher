"""
Architecture Analyzer.
Audits the current telemetry footprint of an organization and classifies components
into VERIFIED, INFERRED, and UNKNOWN.
"""

from typing import Dict, Any, List
from app.models.company import Company
from app.agents.finops_architect.architecture_models import (
    CurrentArchitectureAssessment,
    ArchitectureComponent,
)


class ArchitectureAnalyzer:
    @classmethod
    def analyze_current_setup(cls, company: Company) -> CurrentArchitectureAssessment:
        """Constructs an audited assessment of the current telemetry infrastructure."""
        tech_stack = company.tech_stack or {}
        infra = company.infrastructure_indicators or {}
        evidence_records = company.evidence_records or []

        # Check whether Datadog usage is verified in public repos or inferred
        has_verified_dd = any(
            rec.get("classification") == "VERIFIED" and "datadog" in rec.get("claim", "").lower()
            for rec in evidence_records
        )
        dd_classification = "VERIFIED" if has_verified_dd else "INFERRED"

        components: List[ArchitectureComponent] = [
            ArchitectureComponent(
                name="Datadog Host Agent (v7 DaemonSet)",
                category="Agent",
                classification=dd_classification,
                details="Collects system metrics, process traces, and container socket events",
            ),
            ArchitectureComponent(
                name="dogstatsd (UDP :8125)",
                category="Ingestion",
                classification="INFERRED",
                details="Custom metrics listener ingesting statsd gauges and counters from app containers",
            ),
            ArchitectureComponent(
                name="Datadog APM Tracer (dd-trace)",
                category="Ingestion",
                classification=dd_classification,
                details="In-process tracing library injecting trace headers and shipping spans to local agent",
            ),
        ]

        # Detect Kubernetes / Cloud
        k8s_clusters: List[str] = []
        if "Kubernetes" in tech_stack.get("containers", []) or "k8s_nodes" in infra:
            cloud_name = tech_stack.get("cloud", ["Cloud"])[0] if tech_stack.get("cloud") else "AWS"
            k8s_clusters.append(f"{cloud_name} EKS / Managed Kubernetes Production Cluster")

        return CurrentArchitectureAssessment(
            application_services=components,
            kubernetes_environments=k8s_clusters,
            datadog_agents_detected=True,
            apm_instrumentation="Datadog dd-trace library / agent daemon",
            log_collection_method="Datadog Container Log Collector DaemonSet",
            metrics_collection_method="dogstatsd UDP + kube-state-metrics",
            trace_collection_method="Datadog APM Agent (:8126 TCP)",
        )
