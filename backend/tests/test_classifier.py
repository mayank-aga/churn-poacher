"""
Tests for Signal Classifier.
"""

from app.agents.listener.classifier import SignalClassifier
from app.agents.listener.schemas import NormalizedSignal


def test_classify_pricing_shock():
    sig = NormalizedSignal(
        source="REDDIT",
        source_id="r1",
        source_url="http://reddit.com",
        title="Our Datadog bill jumped by 50% with custom metrics",
        content="We got hit with an unexpected $45,000 overage invoice from Datadog.",
    )
    classified = SignalClassifier.classify(sig)
    assert classified.complaint_category == "PRICING_SHOCK"
    assert classified.sentiment in ["NEGATIVE", "EXTREMELY_NEGATIVE"]
    assert classified.urgency_score >= 0.75
    assert "$45,000" in classified.extracted_evidence.get("financial_figures", [])
    assert "50%" in classified.extracted_evidence.get("percentage_increases", [])


def test_classify_outage():
    sig = NormalizedSignal(
        source="HACKER_NEWS",
        source_id="h1",
        source_url="http://news.ycombinator.com",
        title="Datadog US1 is completely down right now",
        content="Getting 504 Gateway Timeouts across all dashboards and alerts.",
    )
    classified = SignalClassifier.classify(sig)
    assert classified.complaint_category == "OUTAGE"
    assert classified.sentiment in ["NEGATIVE", "EXTREMELY_NEGATIVE"]
    assert classified.urgency_score >= 0.80


def test_classify_migration_intent():
    sig = NormalizedSignal(
        source="REDDIT",
        source_id="r2",
        source_url="http://reddit.com",
        title="Best alternatives to Datadog for Kubernetes?",
        content="We are looking at switching away from Datadog to SigNoz or Grafana using OpenTelemetry.",
    )
    classified = SignalClassifier.classify(sig)
    assert classified.complaint_category == "MIGRATION_INTENT"
    assert classified.urgency_score >= 0.70
    assert classified.relevance_score >= 0.90


def test_positive_mention_not_classified_as_negative():
    sig = NormalizedSignal(
        source="HACKER_NEWS",
        source_id="h2",
        source_url="http://news.ycombinator.com",
        title="We love Datadog APM, it has been an awesome tool",
        content="Great tool for tracing and helped our team debug latency.",
    )
    classified = SignalClassifier.classify(sig)
    assert classified.sentiment == "POSITIVE"
    # Positive signals should have low takeout urgency
    assert classified.urgency_score < 0.60
