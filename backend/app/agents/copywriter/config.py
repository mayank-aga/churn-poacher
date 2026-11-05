"""
Configuration and Tone Guidelines for the Copywriter Agent.
Enforces engineering-led, peer-to-peer tone and anti-spam constraints.
"""

from typing import List, Dict, Any

# Forbidden spammy or sensationalist buzzwords
FORBIDDEN_BUZZWORDS: List[str] = [
    "game-changing",
    "game changing",
    "revolutionary",
    "miracle",
    "silver bullet",
    "rockstar",
    "ninja",
    "10x engineer",
    "unbelievable",
    "insane deal",
    "skyrocket",
    "disruptive magic",
    "secret sauce",
    "no-brainer",
    "growth hack",
]

# Supported executive personas and their primary focus areas
PERSONA_PROFILES: Dict[str, Dict[str, Any]] = {
    "CTO": {
        "title": "Chief Technology Officer",
        "primary_focus": "Strategic TCO, vendor neutrality, OpenTelemetry standard, multi-year lock-in risk",
        "tone": "Strategic, executive, metric-driven",
        "cta": "15-minute executive architectural review",
    },
    "VP_ENGINEERING": {
        "title": "VP of Engineering",
        "primary_focus": "Developer velocity, minimal migration friction, zero-code receiver compatibility (:8126)",
        "tone": "Pragmatic, engineering-focused, risk-averse",
        "cta": "Technical peer review of the dual-shipping PoC blueprint",
    },
    "HEAD_OF_INFRA": {
        "title": "Head of Infrastructure / DevOps Director",
        "primary_focus": "DaemonSet migration, OpenTelemetry Collector pipelines, alert/dashboard parity, ClickHouse performance",
        "tone": "Deeply technical, hands-on, architectural",
        "cta": "Review of the OpenTelemetry Collector YAML and rollout plan",
    },
    "FINOPS_LEAD": {
        "title": "FinOps Lead / Director of Cloud Economics",
        "primary_focus": "Elimination of APM host tax, log re-indexing fees, custom metric overages, 3-year TCO",
        "tone": "Financial, analytical, granular unit economics",
        "cta": "Financial delta and unit-cost comparison session",
    },
}

# Standard enterprise objection catalog
STANDARD_OBJECTIONS = [
    {
        "id": "BANDWIDTH",
        "objection": "We don't have the engineering bandwidth for a complex monitoring migration right now.",
        "talking_points": [
            "Datadog agent receiver (:8126) enables zero-code application changes for existing dd-trace instrumentation.",
            "Dual-shipping OpenTelemetry collector runs alongside existing agents without disrupting application teams.",
            "Total migration engineering effort is modeled at 60-80 engineering hours across a 7-phase timeline.",
        ],
    },
    {
        "id": "DOWNTIME_RISK",
        "objection": "Switching our core observability vendor risks blind spots and production downtime.",
        "talking_points": [
            "Dual-shipping architecture guarantees 100% telemetry continuity with zero production disruption.",
            "Both Datadog and the target challenger receive identical telemetry in parallel during testing.",
            "Datadog is only decommissioned after 100% dashboard, trace, and alert parity is signed off.",
        ],
    },
    {
        "id": "CONTRACT_LOCKIN",
        "objection": "We are locked into an annual contract with Datadog with several months remaining.",
        "talking_points": [
            "Deploying the OpenTelemetry collector now stops unexpected overages and custom metric spikes immediately.",
            "Dual-shipping POC can be completed well ahead of renewal, giving full leverage during contract discussions.",
            "Avoids last-minute renewal pressure by having production-validated alternative ready on day one.",
        ],
    },
    {
        "id": "HISTORICAL_DATA",
        "objection": "We cannot afford to lose our historical metrics, monitors, and custom dashboards.",
        "talking_points": [
            "Existing Datadog dashboards and alerts map directly to OpenTelemetry and PromQL equivalents.",
            "Automated converter scripts translate Datadog monitor JSON into PromQL alert definitions.",
            "Historical log retention can remain in cold storage / S3 while active query pipelines cut over seamlessly.",
        ],
    },
    {
        "id": "SELF_HOSTED_BURDEN",
        "objection": "Managing open source ClickHouse or self-hosted observability creates excessive operational burden.",
        "talking_points": [
            "SigNoz Cloud and Grafana Cloud offer enterprise managed SaaS with 99.9% SLAs and zero infrastructure maintenance.",
            "Managed cloud pricing still delivers 40-70% lower TCO by eliminating host tax and per-host APM penalties.",
            "If self-hosted is preferred, automated Helm charts and operator patterns minimize maintenance overhead.",
        ],
    },
    {
        "id": "STATUS_QUO",
        "objection": "Datadog works fine for us despite the cost, so why change?",
        "talking_points": [
            "Adopting the CNCF OpenTelemetry standard protects your architecture from compounding proprietary lock-in.",
            "Eliminating the per-host tax allows scaling compute (e.g. Kubernetes nodes) without monitoring cost explosion.",
            "Reinvesting $50k-$200k+ in monitoring savings directly into core product engineering.",
        ],
    },
    {
        "id": "ROLLBACK_SAFETY",
        "objection": "What happens if the migration fails halfway through?",
        "talking_points": [
            "Built-in zero-loss rollback strategy: simply disable the target exporter in the OTel collector.",
            "Datadog agent ingestion is never removed until final Stage 7 sign-off.",
            "Zero state loss and zero telemetry downtime guaranteed by dual-pipeline design.",
        ],
    },
]
