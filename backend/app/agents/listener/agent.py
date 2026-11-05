"""
Central Listener Agent Implementation.
Fetches, normalizes, classifies, deduplicates, and persists competitor signals into the database.
"""

import time
from datetime import datetime, timezone
from typing import List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.models.signal import Signal
from app.models.execution_log import AgentExecutionLog
from app.agents.listener.schemas import (
    NormalizedSignal,
    IngestionSummary,
    AdapterStatus,
    ListenerStatusReport,
)
from app.agents.listener.deduplicator import SignalDeduplicator
from app.services.sources.datadog_status import DatadogStatusAdapter
from app.services.sources.hackernews import HackerNewsAdapter
from app.services.sources.reddit import RedditAdapter
from app.services.sources.synthetic_generator import SyntheticSignalGenerator


class ListenerAgent:
    """The Listener Agent continuously ingests public signals indicating Datadog dissatisfaction."""

    def __init__(self):
        self.datadog_status = DatadogStatusAdapter()
        self.hackernews = HackerNewsAdapter()
        self.reddit = RedditAdapter()
        self.last_run_at: Optional[datetime] = None
        self.is_running: bool = False

    async def get_status_report(self, db: AsyncSession) -> ListenerStatusReport:
        """Returns the readiness and configuration status of each ingestion source."""
        adapters = [
            AdapterStatus(
                name="DATADOG_STATUS",
                enabled=True,
                status="AVAILABLE" if await self.datadog_status.is_available() else "UNAVAILABLE",
                details="Polls official public Datadog Statuspage incidents and components",
            ),
            AdapterStatus(
                name="HACKER_NEWS",
                enabled=True,
                status="AVAILABLE" if await self.hackernews.is_available() else "UNAVAILABLE",
                details="Queries official Algolia HN Search API for competitor discussions",
            ),
            AdapterStatus(
                name="REDDIT",
                enabled=self.reddit.is_configured(),
                status="AVAILABLE" if self.reddit.is_configured() else "DISABLED_NO_CREDS",
                details="Reddit OAuth Script App for r/devops, r/sysadmin, r/aws, r/kubernetes",
            ),
            AdapterStatus(
                name="SYNTHETIC_GENERATOR",
                enabled=settings.DEMO_MODE,
                status="AVAILABLE",
                details="Generates high-conviction realistic synthetic signals (is_synthetic=True)",
            ),
        ]

        from sqlalchemy import select, func
        count_res = await db.execute(select(func.count(Signal.id)))
        total_signals = count_res.scalar() or 0

        return ListenerStatusReport(
            is_running=self.is_running,
            demo_mode=settings.DEMO_MODE,
            adapters=adapters,
            last_run_at=self.last_run_at,
            total_signals_stored=total_signals,
        )

    async def run_ingestion_cycle(
        self,
        db: AsyncSession,
        include_synthetic: Optional[bool] = None,
        max_items_per_source: int = 10,
    ) -> IngestionSummary:
        """Runs a complete signal detection, normalization, classification, and persistence cycle."""
        start_time = time.time()
        self.is_running = True
        self.last_run_at = datetime.now(timezone.utc)
        
        include_synth = include_synthetic if include_synthetic is not None else settings.DEMO_MODE
        summary = IngestionSummary()
        collected_signals: List[NormalizedSignal] = []

        logger.info(f"Starting Listener Agent ingestion cycle (demo_mode={include_synth})...")

        # 1. Fetch from Datadog Status Page
        try:
            status_signals = await self.datadog_status.fetch_signals()
            collected_signals.extend(status_signals[:max_items_per_source])
            logger.info(f"Fetched {len(status_signals)} signals from Datadog Status")
        except Exception as e:
            msg = f"Datadog Status fetch error: {str(e)}"
            logger.error(msg)
            summary.errors.append(msg)

        # 2. Fetch from Hacker News API
        try:
            hn_signals = await self.hackernews.fetch_signals()
            collected_signals.extend(hn_signals[:max_items_per_source])
            logger.info(f"Fetched {len(hn_signals)} signals from Hacker News")
        except Exception as e:
            msg = f"Hacker News fetch error: {str(e)}"
            logger.error(msg)
            summary.errors.append(msg)

        # 3. Fetch from Reddit API (only if configured)
        if self.reddit.is_configured():
            try:
                reddit_signals = await self.reddit.fetch_signals()
                collected_signals.extend(reddit_signals[:max_items_per_source])
                logger.info(f"Fetched {len(reddit_signals)} signals from Reddit")
            except Exception as e:
                msg = f"Reddit fetch error: {str(e)}"
                logger.error(msg)
                summary.errors.append(msg)
        else:
            logger.debug("Skipping Reddit (credentials not configured in environment).")

        # 4. Fetch Synthetic Signals if enabled
        if include_synth:
            try:
                synth_signals = SyntheticSignalGenerator.generate_signals(count=4)
                collected_signals.extend(synth_signals)
                logger.info(f"Generated {len(synth_signals)} synthetic signals")
            except Exception as e:
                msg = f"Synthetic generator error: {str(e)}"
                logger.error(msg)
                summary.errors.append(msg)

        summary.total_fetched = len(collected_signals)

        # 5. Deduplicate and Persist
        seen_in_batch: Set[str] = set()
        saved_count = 0
        duplicates_count = 0

        for sig in collected_signals:
            summary.signals_by_source[sig.source] = summary.signals_by_source.get(sig.source, 0) + 1
            summary.signals_by_category[sig.complaint_category] = summary.signals_by_category.get(sig.complaint_category, 0) + 1

            if sig.urgency_score >= 0.75:
                summary.high_urgency_count += 1

            is_dup = await SignalDeduplicator.is_duplicate(sig, db, seen_in_batch=seen_in_batch)
            if is_dup:
                duplicates_count += 1
                continue

            # Map NormalizedSignal into existing SQLAlchemy Signal model
            db_signal = Signal(
                signal_id=sig.source_id,
                source=sig.source,
                original_url=sig.source_url,
                author_handle=sig.author,
                vendor=sig.vendor,
                complaint_category=sig.complaint_category,
                raw_content=sig.content,
                sentiment=sig.sentiment,
                urgency_score=sig.urgency_score,
                extracted_evidence=sig.extracted_evidence,
                is_synthetic=sig.is_synthetic,
                status="NEW",
            )
            db.add(db_signal)
            saved_count += 1

        summary.new_signals_saved = saved_count
        summary.duplicates_skipped = duplicates_count

        # Commit newly saved signals
        await db.commit()

        # 6. Record Agent Execution Log
        duration_ms = int((time.time() - start_time) * 1000)
        summary.execution_time_ms = duration_ms
        self.is_running = False

        log_entry = AgentExecutionLog(
            agent_name="LISTENER",
            signal_id=None,
            status="SUCCESS" if not summary.errors else "PARTIAL_SUCCESS",
            execution_time_ms=duration_ms,
            input_payload={
                "include_synthetic": include_synth,
                "max_items_per_source": max_items_per_source,
            },
            output_payload=summary.model_dump(),
            error_message="; ".join(summary.errors) if summary.errors else None,
        )
        db.add(log_entry)
        await db.commit()

        logger.info(
            f"Listener ingestion cycle complete: {saved_count} saved, {duplicates_count} duplicates skipped "
            f"in {duration_ms}ms"
        )
        return summary
