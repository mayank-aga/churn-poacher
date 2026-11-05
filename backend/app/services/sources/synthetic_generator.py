"""
Synthetic Signal Generator.
Generates realistic, explicitly labeled synthetic signals for demo, development, and testing.
Every record generated MUST have is_synthetic=True.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.agents.listener.schemas import NormalizedSignal
from app.agents.listener.normalizer import SignalNormalizer
from app.agents.listener.classifier import SignalClassifier


class SyntheticSignalGenerator:
    """Produces realistic Datadog competitive takeout signals."""

    SCENARIOS: List[Dict[str, Any]] = [
        {
            "source_id": "synth-dd-pricing-001",
            "source_url": "https://demo.churnpoacher.io/reddit/r/devops/comments/dd_pricing_insane",
            "title": "Datadog billing is completely out of control this month",
            "content": "We just received our monthly Datadog invoice and custom metrics alone added an extra $38,500 without any warning. We are a team of 140 engineers running ~500 nodes on AWS EKS. Has anyone successfully migrated their APM and traces to SigNoz or Grafana with OpenTelemetry?",
            "author": "u/cloud_scale_lead",
            "signal_type": "COMPLAINT",
            "complaint_category": "PRICING_SHOCK",
            "sentiment": "EXTREMELY_NEGATIVE",
            "urgency_score": 0.94,
            "confidence_score": 0.95,
            "relevance_score": 0.98,
            "extracted_evidence": {
                "financial_figures": ["$38,500"],
                "percentage_increases": ["45%"],
                "products_mentioned": ["custom metrics", "apm"],
                "inferred_nodes": 500,
                "inferred_engineers": 140,
            },
            "age_hours": 2,
        },
        {
            "source_id": "synth-dd-outage-002",
            "source_url": "https://demo.churnpoacher.io/hn/item/38891240",
            "title": "Datadog US1 dashboard and alerts down during Black Friday deployment",
            "content": "Is anyone else getting 504 Gateway Timeouts on Datadog US1? None of our alert monitors are triggering while our checkout service is throwing errors. We are flying completely blind right now. This is the second outage in 6 weeks.",
            "author": "sre_director_ny",
            "signal_type": "COMPLAINT",
            "complaint_category": "OUTAGE",
            "sentiment": "EXTREMELY_NEGATIVE",
            "urgency_score": 0.96,
            "confidence_score": 0.92,
            "relevance_score": 0.90,
            "extracted_evidence": {
                "region": "US1",
                "outage_duration_est": "2 hours",
                "products_mentioned": ["alerts", "dashboards"],
            },
            "age_hours": 1,
        },
        {
            "source_id": "synth-dd-migration-003",
            "source_url": "https://demo.churnpoacher.io/reddit/r/kubernetes/comments/migrating_away_from_dd",
            "title": "Looking for architecture blueprints: Migrating from Datadog Agent to OpenTelemetry Collector",
            "content": "Our leadership just mandated a 40% reduction in monitoring spend by Q2. Currently spending ~$22,000/month on Datadog host monitoring and logs. We want to switch to SigNoz or self-hosted Grafana Tempo/Mimir. How do we dual-ship telemetry without downtime during migration?",
            "author": "u/platform_architect_99",
            "signal_type": "COMPLAINT",
            "complaint_category": "MIGRATION_INTENT",
            "sentiment": "NEGATIVE",
            "urgency_score": 0.88,
            "confidence_score": 0.96,
            "relevance_score": 0.99,
            "extracted_evidence": {
                "financial_figures": ["$22,000"],
                "percentage_increases": ["40%"],
                "products_mentioned": ["logs", "apm", "agent"],
                "target_challengers": ["SigNoz", "Grafana"],
            },
            "age_hours": 5,
        },
        {
            "source_id": "synth-dd-reliability-004",
            "source_url": "https://demo.churnpoacher.io/hn/item/38914421",
            "title": "Datadog log ingestion latency spiking over 15 minutes",
            "content": "Anyone else experiencing huge lag on log ingestion with Datadog? By the time logs appear in the dashboard, the incident has already escalated. We pay premium enterprise pricing for near real-time observability.",
            "author": "devops_guy_sf",
            "signal_type": "COMPLAINT",
            "complaint_category": "RELIABILITY",
            "sentiment": "NEGATIVE",
            "urgency_score": 0.78,
            "confidence_score": 0.88,
            "relevance_score": 0.82,
            "extracted_evidence": {
                "products_mentioned": ["logs"],
                "delay_minutes": 15,
            },
            "age_hours": 12,
        },
    ]

    @classmethod
    def generate_signals(cls, count: int = 4) -> List[NormalizedSignal]:
        """Generates realistic synthetic signals with explicit is_synthetic=True."""
        now = datetime.now(timezone.utc)
        signals: List[NormalizedSignal] = []

        for idx, scenario in enumerate(cls.SCENARIOS[:count]):
            pub_time = now - timedelta(hours=scenario.get("age_hours", idx + 1))
            raw_payload = dict(scenario)
            raw_payload["published_at"] = pub_time
            raw_payload["is_synthetic"] = True
            
            normalized = SignalNormalizer.normalize_synthetic(raw_payload)
            classified = SignalClassifier.classify(normalized)
            signals.append(classified)

        return signals
