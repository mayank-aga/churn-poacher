"""
Signal Deduplicator.
Generates deterministic fingerprints and checks against the database to guarantee idempotency.
"""

import hashlib
from typing import Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.signal import Signal
from app.agents.listener.schemas import NormalizedSignal


class SignalDeduplicator:
    @staticmethod
    def generate_fingerprint(signal: NormalizedSignal) -> str:
        """Generates a stable, unique fingerprint string for the signal."""
        # Primary key based on source and source_id
        if signal.source and signal.source_id:
            key = f"{signal.source.upper()}:{signal.source_id.strip()}"
        elif signal.source_url:
            key = f"URL:{signal.source_url.strip().lower()}"
        else:
            # Fallback to content hash
            text_snippet = f"{signal.title}:{signal.content[:200]}"
            key = f"CONTENT:{text_snippet.strip().lower()}"
            
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]

    @classmethod
    async def is_duplicate(
        cls,
        signal: NormalizedSignal,
        db: AsyncSession,
        seen_in_batch: Optional[Set[str]] = None,
    ) -> bool:
        """Checks if the signal already exists in the current batch or database."""
        # 1. Check in-memory batch cache
        fingerprint = cls.generate_fingerprint(signal)
        if seen_in_batch is not None:
            if fingerprint in seen_in_batch or signal.source_id in seen_in_batch:
                return True

        # 2. Query database for matching signal_id
        query = select(Signal.id).where(
            (Signal.signal_id == signal.source_id) | 
            (Signal.signal_id == fingerprint) |
            (Signal.original_url == signal.source_url)
        ).limit(1)
        
        result = await db.execute(query)
        exists = result.scalar_one_or_none() is not None
        
        if not exists and seen_in_batch is not None:
            seen_in_batch.add(fingerprint)
            seen_in_batch.add(signal.source_id)
            
        return exists
