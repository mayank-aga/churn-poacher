"""
Tests for Signal Ingestion Source Adapters.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.sources.datadog_status import DatadogStatusAdapter
from app.services.sources.hackernews import HackerNewsAdapter
from app.services.sources.reddit import RedditAdapter
from app.services.sources.synthetic_generator import SyntheticSignalGenerator


@pytest.mark.asyncio
async def test_datadog_status_adapter_parsing():
    sample_response = {
        "page": {"id": "138746", "name": "Datadog"},
        "incidents": [
            {
                "id": "inc-12345",
                "name": "Degraded Metrics Ingestion in US1",
                "status": "investigating",
                "impact": "major",
                "created_at": "2026-11-05T12:00:00Z",
                "shortlink": "https://status.datadoghq.com/incidents/inc-12345",
                "incident_updates": [
                    {"body": "We are observing increased latency in custom metric ingestion."}
                ],
                "components": [{"name": "Metrics - US1"}],
            }
        ]
    }

    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_http:
        mock_http.return_value.__aenter__.return_value = mock_client
        adapter = DatadogStatusAdapter()
        signals = await adapter.fetch_signals()

        assert len(signals) == 1
        sig = signals[0]
        assert sig.source == "DATADOG_STATUS"
        assert sig.source_id == "dd-status-inc-12345"
        assert sig.complaint_category == "VENDOR_INCIDENT"
        assert sig.urgency_score >= 0.85
        assert sig.is_synthetic is False


@pytest.mark.asyncio
async def test_hackernews_adapter_parsing():
    sample_response = {
        "hits": [
            {
                "objectID": "887766",
                "title": "Why our Datadog bill doubled after moving to Kubernetes",
                "story_text": "We ran into huge overage fees for custom metrics.",
                "url": "https://blog.tech.com/datadog-bill",
                "author": "techlead_dan",
                "created_at": "2026-11-04T15:30:00Z",
                "points": 145,
                "num_comments": 89,
            },
            {
                "objectID": "112233",
                "title": "Unrelated post about Redis",
                "story_text": "No competitor mentions here.",
                "author": "other_guy",
            }
        ]
    }

    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_response
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_http:
        mock_http.return_value.__aenter__.return_value = mock_client
        adapter = HackerNewsAdapter()
        signals = await adapter.fetch_signals(queries=["datadog bill"])

        # Should include the Datadog hit and filter out the unrelated Redis hit
        assert len(signals) == 1
        sig = signals[0]
        assert sig.source == "HACKER_NEWS"
        assert sig.source_id == "hn-887766"
        assert sig.complaint_category == "PRICING_SHOCK"
        assert sig.is_synthetic is False


def test_reddit_adapter_missing_credentials_graceful_handling():
    # When client_id is None, adapter must gracefully report unconfigured
    adapter = RedditAdapter(client_id=None, client_secret=None)
    assert adapter.is_configured() is False


@pytest.mark.asyncio
async def test_reddit_adapter_fetches_empty_when_unconfigured():
    adapter = RedditAdapter(client_id=None, client_secret=None)
    signals = await adapter.fetch_signals()
    assert signals == []


def test_synthetic_generator_strict_labeling():
    signals = SyntheticSignalGenerator.generate_signals(count=3)
    assert len(signals) == 3
    for s in signals:
        assert s.is_synthetic is True
        assert s.source == "SYNTHETIC"
        assert s.published_at.tzinfo is not None
        assert s.urgency_score > 0.0
