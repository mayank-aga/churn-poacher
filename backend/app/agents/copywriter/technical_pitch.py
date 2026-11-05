"""
Technical Migration Pitch Generator for the Copywriter Agent.
Produces deep-dive technical briefing collateral covering OpenTelemetry architecture,
receiver compatibility, dual-shipping strategy, and dashboard/alert parity.
"""

from typing import Dict, Any
from app.agents.copywriter.schemas import TechnicalMigrationPitch


class TechnicalPitchWriter:
    """Generates an in-depth technical migration document and slide-deck narrative."""

    @classmethod
    def generate_pitch(
        cls,
        context: Dict[str, Any],
        finops_data: Dict[str, Any],
        arch_data: Dict[str, Any],
    ) -> TechnicalMigrationPitch:
        """Generates comprehensive technical migration brief."""
        company_name = context["company_name"]
        target_challenger = context["target_challenger"]
        challenger_tech = context["challenger_tech"]

        base_scenario = finops_data.get("scenarios", {}).get("BASE") or finops_data.get("base_scenario") or {}
        annual_savings = base_scenario.get("signoz_cloud_annual_savings", 84000.0)
        savings_pct = base_scenario.get("signoz_cloud_savings_pct", 70.0)
        payback_months = base_scenario.get("payback_period_months", 1.8)
        savings_str = f"${annual_savings:,.0f}"

        arch_comparison = {
            "Agent Architecture": "Datadog uses a proprietary closed-source daemonset; target uses standard CNCF OpenTelemetry Collector.",
            "Tracing Ingestion": "Datadog relies on dd-trace libraries; OTel collector provides a Datadog-compatible receiver (:8126) for zero-code ingestion.",
            "Storage Engine": "Datadog uses proprietary multi-tier backend with aggressive retention charges; target utilizes high-performance ClickHouse columnar storage or Prometheus/Loki.",
            "Cost Model": "Datadog levies a compounding host tax + per-APM-host charge + custom metric fees; target utilizes pure volume-based ingestion with zero host tax.",
        }

        zero_code = (
            "The OpenTelemetry Collector distribution includes a native Datadog trace receiver "
            "(`receiver: datadog: endpoint: 0.0.0.0:8126`). Existing microservices instrumented with `dd-trace` "
            "(Python, Node.js, Go, Java, Ruby) continue sending traces to `localhost:8126` or the daemonset service. "
            "The collector translates Datadog spans into standard OTel trace format in-memory with near-zero latency, "
            "eliminating the need to refactor application SDKs prior to migration."
        )

        dual_shipping = (
            "During the migration validation window, the OpenTelemetry Collector acts as an intelligent router. "
            "By configuring dual exporters (`exporters: [datadog, otlp/target]`), both Datadog and the target challenger "
            "receive identical trace, metric, and log data simultaneously. This enables real-time verification of "
            "sampling rates, latency calculations, and metric accuracy with zero risk of telemetry gaps."
        )

        parity = (
            "1. **Monitors & Alerts**: Datadog monitor definitions map systematically to PromQL / SigNoz alert rules. "
            "Threshold and change alerts are mirrored in the target platform to verify identical trigger behavior. "
            "2. **Dashboards**: Core infrastructure, Kubernetes, and APM service dashboards are imported using standard "
            "Grafana JSON / SigNoz dashboard specifications. "
            "3. **Log Pipelines**: Log parsing, grok rules, and facet indexing are replicated via OpenTelemetry collector "
            "transform processors and ClickHouse materialize views."
        )

        timeline = (
            "The migration follows a structured 7-stage phased rollout spanning approximately 4 to 6 weeks, "
            "requiring an estimated 60 to 80 total engineering hours: "
            "Phase 1: Architecture Review & Collector Sandbox (3 days) | "
            "Phase 2: Collector DaemonSet Deployment & Dual-Shipping (5 days) | "
            "Phase 3: APM Ingestion & Port 8126 Compatibility Validation (5 days) | "
            "Phase 4: Dashboard & Alert Rule Parity Migration (7 days) | "
            "Phase 5: Log Pipeline & Retention Cutover (5 days) | "
            "Phase 6: Parallel Production Validation & Drift Audit (7 days) | "
            "Phase 7: Datadog Decommission & Agent Cleanup (2 days)."
        )

        full_markdown = f"""# Technical Migration Brief: Datadog -> {target_challenger}
**Prepared for**: Engineering Leadership at {company_name}  
**Focus**: Zero-Disruption OpenTelemetry Migration & Telemetry Cost Optimization  
**Modeled ROI**: Estimated ~{savings_pct:.0f}% Spend Reduction (~{savings_str}/year) | Payback: ~{payback_months:.1f} months

---

## 1. Executive Summary & Architectural Motivation
Enterprise telemetry at {company_name} is currently bound to proprietary Datadog agents and pricing constructs. 
As infrastructure scales, host-based licensing models impose an artificial 'tax' on ephemeral nodes, auto-scaling groups, 
and microservice architectures.

Transitioning to **{challenger_tech}** decouples your infrastructure from vendor lock-in by standardizing on the 
CNCF OpenTelemetry standard while reducing monitoring operational expenditure by an estimated **{savings_str}/year**.

---

## 2. Architecture Comparison

| Architectural Dimension | Legacy (Datadog) | Target ({target_challenger}) |
| :--- | :--- | :--- |
| **Agent / Collector** | Proprietary Datadog Agent 7 | CNCF OpenTelemetry Collector Contrib |
| **Tracing Protocol** | Proprietary `dd-trace` format | OpenTelemetry Protocol (OTLP / gRPC) |
| **Receiver Compatibility**| Proprietary agent only | Native Datadog Receiver on `:8126` |
| **Storage Backend** | Proprietary multi-tier SaaS | Distributed ClickHouse columnar storage |
| **Licensing Metric** | Per-Host + Per-APM + Custom Metrics | Pure usage/ingestion-based (Zero Host Tax) |

---

## 3. Zero-Code Migration Path via Port `:8126`
{zero_code}

```yaml
# OpenTelemetry Collector Datadog Receiver Configuration
receivers:
  datadog:
    endpoint: 0.0.0.0:8126
    read_timeout: 60s

processors:
  batch:
    send_batch_size: 10000
    timeout: 10s

exporters:
  datadog:
    api:
      key: "${{env:DD_API_KEY}}"
  otlp/{target_challenger.lower().split()[0]}:
    endpoint: "ingest.signoz.cloud:443"
    headers:
      "signoz-access-token": "${{env:SIGNOZ_API_KEY}}"

service:
  pipelines:
    traces:
      receivers: [datadog]
      processors: [batch]
      exporters: [datadog, otlp/{target_challenger.lower().split()[0]}]
```

---

## 4. Risk-Free Dual-Shipping Strategy
{dual_shipping}

---

## 5. Alert & Dashboard Parity Validation
{parity}

---

## 6. Phased Implementation Timeline & Effort
{timeline}

---

## 7. Rollback Safety Guarantee
If any anomaly, metric drift, or incompatibility occurs during parallel validation, rollback requires a single configuration change:
disable the target exporter in the OpenTelemetry collector. Datadog agent pipelines remain fully operational throughout 
Stages 1 through 6 until final decommission sign-off.
"""

        return TechnicalMigrationPitch(
            title=f"Technical Migration Brief: Datadog to {target_challenger}",
            target_audience="CTO, VP of Engineering, Head of Infrastructure",
            architecture_comparison=arch_comparison,
            zero_code_migration_path=zero_code,
            dual_shipping_poc=dual_shipping,
            alert_and_dashboard_parity=parity,
            timeline_and_effort=timeline,
            full_pitch_markdown=full_markdown.strip(),
        )
