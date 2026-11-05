"""
Tests for Signal Normalizer.
"""

from datetime import timezone
from app.agents.listener.normalizer import SignalNormalizer


def test_normalize_datadog_incident():
    raw = {
        "id": "inc-99",
        "name": "Major APM Outage",
        "status": "investigating",
        "impact": "critical",
        "created_at": "2026-11-05T10:00:00Z",
        "shortlink": "https://status.datadoghq.com/incidents/inc-99",
        "incident_updates": [{"body": "Investigating high error rates."}],
        "components": [{"name": "APM Ingestion"}],
    }
    sig = SignalNormalizer.normalize_datadog_incident(raw)
    assert sig.source == "DATADOG_STATUS"
    assert sig.source_id == "dd-status-inc-99"
    assert sig.signal_type == "VENDOR_INCIDENT"
    assert sig.published_at.tzinfo == timezone.utc
    assert sig.urgency_score == 0.90


def test_normalize_hackernews_item():
    raw = {
        "objectID": "554433",
        "title": "Datadog is too expensive for small startups",
        "story_text": "We cannot afford $3,000/mo on monitoring.",
        "url": "https://news.ycombinator.com/item?id=554433",
        "author": "founder_alice",
        "created_at": "2026-11-04T08:00:00Z",
    }
    sig = SignalNormalizer.normalize_hackernews_item(raw)
    assert sig.source == "HACKER_NEWS"
    assert sig.source_id == "hn-554433"
    assert sig.author == "founder_alice"
    assert sig.published_at.tzinfo == timezone.utc


def test_normalize_reddit_post():
    raw = {
        "id": "post-777",
        "title": "Leaving Datadog for SigNoz",
        "selftext": "Our contract renewal increased by 35%. Migrating to OpenTelemetry.",
        "permalink": "/r/devops/comments/post-777/leaving_datadog",
        "author": "sre_bob",
        "created_utc": 1730800000.0,
        "subreddit": "devops",
    }
    sig = SignalNormalizer.normalize_reddit_post(raw)
    assert sig.source == "REDDIT"
    assert sig.source_id == "reddit-post-777"
    assert sig.author == "u/sre_bob"
    assert sig.published_at.tzinfo == timezone.utc


def test_normalize_synthetic():
    raw = {
        "source_id": "synth-01",
        "title": "Test Synthetic Alert",
        "content": "Realistic text body",
        "is_synthetic": True,
    }
    sig = SignalNormalizer.normalize_synthetic(raw)
    assert sig.is_synthetic is True
    assert sig.source == "SYNTHETIC"
    assert sig.published_at.tzinfo == timezone.utc
