"""
Cost Estimator.
Derives and validates telemetry volume inputs based on company size, signal evidence,
and cloud footprint indicators.
"""

from typing import List, Dict, Any, Tuple
from app.agents.finops_architect.financial_models import InfrastructureInput


class CostEstimator:
    @classmethod
    def derive_telemetry_inputs(
        cls,
        estimated_size: str,
        infrastructure_indicators: Dict[str, Any] = None,
        extracted_evidence: Dict[str, Any] = None,
    ) -> List[InfrastructureInput]:
        """Derives quantified telemetry inputs with explicit source and confidence tracking."""
        infra = infrastructure_indicators or {}
        evidence = extracted_evidence or {}

        # 1. Monitored Hosts / Nodes
        if "inferred_nodes" in evidence:
            hosts = float(evidence["inferred_nodes"])
            source = "SignalEvidence"
            confidence = 0.85
            is_verified = False
        elif "k8s_nodes" in infra:
            hosts = float(infra["k8s_nodes"])
            source = "ProfileInferred"
            confidence = 0.80
            is_verified = False
        else:
            # Scale conservatively based on employee size
            size_lower = estimated_size.lower()
            if "500-1000" in size_lower or "250-1000" in size_lower:
                hosts = 350.0
            elif "100-250" in size_lower or "50-250" in size_lower:
                hosts = 120.0
            elif "10-50" in size_lower:
                hosts = 35.0
            else:
                hosts = 75.0
            source = "CompanySizeHeuristic"
            confidence = 0.65
            is_verified = False

        # 2. APM Hosts (typically ~70% of hosts in microservice environments)
        apm_hosts = round(hosts * 0.70, 0)

        # 3. Custom Metrics (Standard Kubernetes ratio: ~80-120 metrics/host)
        custom_metrics = round(hosts * 100.0, 0)

        # 4. Monthly Log Volume (approx 25 GB / host / month)
        log_gb = round(hosts * 25.0, 0)

        # 5. Monthly Trace Volume (approx 15 GB / host / month)
        trace_gb = round(hosts * 15.0, 0)

        return [
            InfrastructureInput(
                name="monitored_hosts",
                value=hosts,
                unit="hosts",
                source=source,
                confidence=confidence,
                is_verified=is_verified,
            ),
            InfrastructureInput(
                name="apm_hosts",
                value=apm_hosts,
                unit="hosts",
                source="DerivedRatio",
                confidence=0.75,
                is_verified=False,
            ),
            InfrastructureInput(
                name="custom_metrics",
                value=custom_metrics,
                unit="metrics",
                source="TelemetryFootprintRatio",
                confidence=0.70,
                is_verified=False,
            ),
            InfrastructureInput(
                name="monthly_log_gb",
                value=log_gb,
                unit="GB",
                source="StandardWorkloadRatio",
                confidence=0.70,
                is_verified=False,
            ),
            InfrastructureInput(
                name="monthly_trace_gb",
                value=trace_gb,
                unit="GB",
                source="StandardWorkloadRatio",
                confidence=0.70,
                is_verified=False,
            ),
        ]
