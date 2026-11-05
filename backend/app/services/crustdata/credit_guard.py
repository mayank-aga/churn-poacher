"""
Crustdata Credit Guard.
Protects against credit depletion by inspecting account balances before paid calls
and strictly enforcing configurable safety thresholds.
"""

import time
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from app.services.crustdata.schemas import CrustdataCreditsInfo, EnrichmentLevel
from app.services.crustdata.exceptions import CrustdataCreditDepletedError


class CreditGuard:
    """Enforces safety thresholds and audits credits before invoking paid Crustdata endpoints."""

    # Cached balance to avoid making gratuitous balance queries
    _cached_credits: Optional[CrustdataCreditsInfo] = None
    _last_checked_timestamp: float = 0.0
    CACHE_TTL_SECONDS: float = 60.0

    # Pricing estimates based on official Crustdata documentation
    OPERATION_COSTS = {
        EnrichmentLevel.LEVEL_1_SEARCH: 0.5,       # Candidate search: ~0.5 - 1 credit
        EnrichmentLevel.LEVEL_2_STANDARD: 2.0,     # Cached database enrichment: ~1 - 2 credits
        EnrichmentLevel.LEVEL_3_DEEP: 15.0,        # Real-time web crawler: ~10 - 25 credits
    }

    @classmethod
    def estimate_cost(cls, level: EnrichmentLevel) -> float:
        """Returns the estimated credit cost for an enrichment level."""
        return cls.OPERATION_COSTS.get(level, 2.0)

    @classmethod
    def is_cache_valid(cls) -> bool:
        if cls._cached_credits is None:
            return False
        return (time.time() - cls._last_checked_timestamp) < cls.CACHE_TTL_SECONDS

    @classmethod
    def update_cached_credits(cls, credits_info: CrustdataCreditsInfo) -> None:
        cls._cached_credits = credits_info
        cls._last_checked_timestamp = time.time()
        logger.debug(
            f"Crustdata credits updated: remaining={credits_info.remaining_credits:.1f}, "
            f"used={credits_info.used_credits:.1f}"
        )

    @classmethod
    def get_cached_credits(cls) -> Optional[CrustdataCreditsInfo]:
        if cls.is_cache_valid():
            return cls._cached_credits
        return None

    @classmethod
    def verify_budget_can_proceed(
        cls,
        estimated_cost: float,
        credits_info: Optional[CrustdataCreditsInfo] = None,
    ) -> bool:
        """
        Validates if the account has enough remaining credits above the minimum safety floor.
        Raises CrustdataCreditDepletedError if depleted.
        """
        active_credits = credits_info or cls._cached_credits
        if not active_credits:
            # If no balance information has been fetched yet, let caller fetch it
            return True

        min_threshold = float(settings.CRUSTDATA_MIN_CREDIT_THRESHOLD)
        remaining = active_credits.remaining_credits

        if remaining - estimated_cost < min_threshold:
            logger.warning(
                f"Credit guard blocked operation: remaining {remaining:.1f} - cost {estimated_cost:.1f} "
                f"< threshold {min_threshold:.1f}"
            )
            raise CrustdataCreditDepletedError(
                current_balance=remaining,
                required_credits=estimated_cost,
                min_threshold=min_threshold,
            )

        return True
