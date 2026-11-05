"""
Tests for Signal Deduplicator.
"""

import pytest
from app.agents.listener.deduplicator import SignalDeduplicator
from app.agents.listener.schemas import NormalizedSignal
from app.db.session import init_db, AsyncSessionLocal
from app.models.signal import Signal


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


def test_fingerprint_generation():
    sig1 = NormalizedSignal(
        source="REDDIT",
        source_id="post-abc",
        source_url="https://reddit.com/r/devops/abc",
        content="Test content",
    )
    sig2 = NormalizedSignal(
        source="REDDIT",
        source_id="post-abc",
        source_url="https://reddit.com/r/devops/abc",
        content="Different content but same source and source_id",
    )
    fp1 = SignalDeduplicator.generate_fingerprint(sig1)
    fp2 = SignalDeduplicator.generate_fingerprint(sig2)
    assert fp1 == fp2
    assert len(fp1) == 32


@pytest.mark.asyncio
async def test_duplicate_detection_in_database():
    async with AsyncSessionLocal() as session:
        # Save a signal to DB
        existing_sig = Signal(
            signal_id="unique-dedup-id-1",
            source="HACKER_NEWS",
            original_url="https://news.ycombinator.com/item?id=99999",
            complaint_category="OUTAGE",
            raw_content="Datadog outage test",
            is_synthetic=True,
        )
        session.add(existing_sig)
        await session.commit()

        # Check duplicate
        incoming = NormalizedSignal(
            source="HACKER_NEWS",
            source_id="unique-dedup-id-1",
            source_url="https://news.ycombinator.com/item?id=99999",
            content="Datadog outage test",
        )
        is_dup = await SignalDeduplicator.is_duplicate(incoming, session)
        assert is_dup is True

        # Check non-duplicate
        non_dup = NormalizedSignal(
            source="HACKER_NEWS",
            source_id="brand-new-id-2",
            source_url="https://news.ycombinator.com/item?id=100000",
            content="New signal",
        )
        is_dup_new = await SignalDeduplicator.is_duplicate(non_dup, session)
        assert is_dup_new is False
