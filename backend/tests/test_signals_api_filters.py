"""
Regression tests for Signal API filter robustness and HTML sanitization.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.agents.listener.normalizer import strip_html
from app.models.signal import Signal
from app.db.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_signals_api_ignores_undefined_and_null_filters():
    """Verify that literal 'undefined' or 'null' from frontend URLSearchParams does not zero out results."""
    # Seed 2 test signals
    async with AsyncSessionLocal() as db:
        s1 = Signal(
            signal_id="sig-test-1",
            source="DATADOG_STATUS",
            original_url="https://status.datadoghq.com/1",
            raw_content="<p>Datadog incident report with HTML</p>",
            complaint_category="OUTAGE",
            urgency_score=0.8,
            is_synthetic=False,
        )
        s2 = Signal(
            signal_id="sig-test-2",
            source="HACKER_NEWS",
            original_url="https://news.ycombinator.com/2",
            raw_content="Datadog pricing shock discussion",
            complaint_category="PRICING_SHOCK",
            urgency_score=0.9,
            is_synthetic=False,
        )
        db.add_all([s1, s2])
        await db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Unfiltered call
        res_all = await client.get("/api/v1/signals?limit=100")
        assert res_all.status_code == 200
        all_signals = res_all.json()
        assert len(all_signals) == 2

        # 2. Call with source=undefined&complaint_category=undefined (mimicking buggy frontend serializer)
        res_undefined = await client.get("/api/v1/signals?source=undefined&complaint_category=undefined&limit=100")
        assert res_undefined.status_code == 200
        data_undefined = res_undefined.json()
        # Must return the 2 signals rather than 0
        assert len(data_undefined) == len(all_signals)

        # 3. Call with source=null&complaint_category=null
        res_null = await client.get("/api/v1/signals?source=null&complaint_category=null&limit=100")
        assert res_null.status_code == 200
        assert len(res_null.json()) == len(all_signals)

        # 4. Valid filters work properly
        res_filtered_source = await client.get("/api/v1/signals?source=DATADOG_STATUS&limit=100")
        assert res_filtered_source.status_code == 200
        assert len(res_filtered_source.json()) == 1
        assert res_filtered_source.json()[0]["source"] == "DATADOG_STATUS"

        res_filtered_cat = await client.get("/api/v1/signals?complaint_category=PRICING_SHOCK&limit=100")
        assert res_filtered_cat.status_code == 200
        assert len(res_filtered_cat.json()) == 1
        assert res_filtered_cat.json()[0]["complaint_category"] == "PRICING_SHOCK"


def test_strip_html_utility():
    """Verify HTML tags and HTML entities are cleanly stripped."""
    raw = "<p><small>Oct 28, 18:39 UTC</small><br><strong>Resolved</strong> - Issue is resolved.</p>"
    clean = strip_html(raw)
    assert "<" not in clean
    assert ">" not in clean
    assert "Oct 28, 18:39 UTC Resolved - Issue is resolved." in clean

    raw_entities = "Mike and Warren here! We&#x27;ve been building &quot;HyperDX&quot; &amp; others."
    clean_entities = strip_html(raw_entities)
    assert clean_entities == "Mike and Warren here! We've been building \"HyperDX\" & others."
