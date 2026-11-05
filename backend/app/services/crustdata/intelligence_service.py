"""
Generic Crustdata Intelligence Extraction Service.
Implements Entity Resolution, Three-Level Extraction (Search, Standard Enrichment, Deep Enrichment),
Multi-tiered Caching, Provenance Enforcement, and Credit Safety.
"""

import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc

from app.core.config import settings
from app.core.logging import logger
from app.models.intelligence import (
    IntelligenceEntity,
    IntelligenceSearch,
    IntelligenceEvidence,
)
from app.services.crustdata.client import CrustdataClient
from app.services.crustdata.credit_guard import CreditGuard
from app.services.crustdata.exceptions import (
    CrustdataAmbiguousEntityError,
    CrustdataCreditDepletedError,
)
from app.services.crustdata.schemas import (
    EntityType,
    EnrichmentLevel,
    VerificationClassification,
    EntityCandidate,
    EntitySearchResponse,
    CompanyIntelligenceProfile,
    PersonIntelligenceProfile,
    DeepEnrichmentCostEstimate,
    CrustdataCreditsInfo,
)


class CrustdataIntelligenceService:
    """Core intelligence orchestration layer for company and person intelligence."""

    def __init__(self, client: Optional[CrustdataClient] = None):
        self.client = client or CrustdataClient()

    @staticmethod
    def detect_entity_type(query: str) -> EntityType:
        """
        Automatically determines whether an input query represents a Company or a Person.
        Follows strict pattern heuristics.
        """
        if not query or not query.strip():
            return EntityType.UNKNOWN

        q = query.strip()
        q_lower = q.lower()

        # 1. URL pattern detection
        if "linkedin.com/company/" in q_lower:
            return EntityType.COMPANY
        if "linkedin.com/in/" in q_lower or "twitter.com/" in q_lower or "x.com/" in q_lower:
            return EntityType.PERSON
        if re.search(r"^https?://[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}", q_lower):
            return EntityType.COMPANY

        # 2. Domain pattern detection (e.g. spacex.com, openai.io, nvidia.ai)
        if re.match(r"^[a-zA-Z0-9\-]+(\.[a-zA-Z]{2,})+$", q_lower):
            return EntityType.COMPANY

        # 3. Explicit corporate legal suffixes or company keywords
        company_suffixes = [
            r"\binc\b", r"\bllc\b", r"\bltd\b", r"\bcorp\b", r"\bgmbh\b",
            r"\btechnologies\b", r"\bsystems\b", r"\blabs\b", r"\bcapital\b",
            r"\bpartners\b", r"\bsoftware\b", r"\bventures\b", r"\bgroup\b"
        ]
        for suffix in company_suffixes:
            if re.search(suffix, q_lower):
                return EntityType.COMPANY

        # 4. Single-word known organizations (e.g., Datadog, SpaceX, OpenAI, NVIDIA, Tesla, Google)
        known_orgs = ["datadog", "spacex", "openai", "nvidia", "tesla", "google", "microsoft", "amazon", "apple", "signoz", "hyperdx"]
        if q_lower in known_orgs:
            return EntityType.COMPANY

        # 5. Multi-word string without corporate words -> Likely Person Name (e.g. "Elon Musk", "Sam Altman")
        words = q.split()
        if len(words) >= 2 and all(w[0].isupper() for w in words if w.isalpha()):
            return EntityType.PERSON

        # Fallback to UNKNOWN (Search will test both or ask user)
        return EntityType.UNKNOWN

    async def search_candidates(
        self,
        db: AsyncSession,
        query: str,
        entity_type: Optional[EntityType] = None,
        limit: int = 5,
    ) -> EntitySearchResponse:
        """
        LEVEL 1 — SEARCH
        Identifies matching companies or people, returns candidates, and minimizes credit consumption.
        Never automatically enriches an ambiguous entity.
        """
        detected_type = entity_type or self.detect_entity_type(query)
        candidates: List[EntityCandidate] = []
        credits_consumed = CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_1_SEARCH)

        if detected_type == EntityType.COMPANY:
            candidates = await self.client.search_company_candidates(query, limit=limit)
        elif detected_type == EntityType.PERSON:
            candidates = await self.client.search_person_candidates(query, limit=limit)
        else:
            # Query both if ambiguous or unknown
            comp_cands = await self.client.search_company_candidates(query, limit=limit)
            person_cands = await self.client.search_person_candidates(query, limit=limit)
            candidates = comp_cands + person_cands
            if comp_cands and not person_cands:
                detected_type = EntityType.COMPANY
            elif person_cands and not comp_cands:
                detected_type = EntityType.PERSON

        # Determine ambiguity: multiple distinct candidate identities
        is_ambiguous = len(candidates) > 1

        # Audit search query in DB
        search_record = IntelligenceSearch(
            id=str(uuid.uuid4()),
            search_query=query,
            entity_type=detected_type.value,
            search_status="AMBIGUOUS" if is_ambiguous else ("COMPLETED" if candidates else "NO_MATCH"),
            candidates=[c.model_dump(mode="json") for c in candidates],
            credits_consumed=credits_consumed,
            is_mock=any(c.is_mock for c in candidates),
        )
        db.add(search_record)
        await db.commit()

        return EntitySearchResponse(
            query=query,
            detected_type=detected_type,
            candidates=candidates,
            is_ambiguous=is_ambiguous,
            credits_consumed=credits_consumed,
            is_mock=any(c.is_mock for c in candidates),
        )

    async def enrich_entity(
        self,
        db: AsyncSession,
        identifier: str,
        entity_type: EntityType,
        level: EnrichmentLevel = EnrichmentLevel.LEVEL_2_STANDARD,
        force_refresh: bool = False,
        confirmation_confirmed: bool = False,
    ) -> Union[CompanyIntelligenceProfile, PersonIntelligenceProfile, DeepEnrichmentCostEstimate]:
        """
        LEVEL 2 — STANDARD ENRICHMENT & LEVEL 3 — DEEP ENRICHMENT.
        - Checks local database cache first (7-day TTL).
        - If LEVEL 3 DEEP is requested without confirmation_confirmed=True, returns DeepEnrichmentCostEstimate.
        - Persists extracted profile and evidence provenance.
        """
        clean_id = identifier.strip().lower()

        # Safety Gate: LEVEL 3 DEEP ENRICHMENT requires explicit confirmation
        if level == EnrichmentLevel.LEVEL_3_DEEP and not confirmation_confirmed:
            return await self.estimate_deep_enrichment_cost(identifier, entity_type)

        # 1. Local Database Cache Check (Prevent duplicate API calls & save credits)
        if not force_refresh and level != EnrichmentLevel.LEVEL_3_DEEP:
            cached_entity = await self._find_cached_entity(db, clean_id, entity_type)
            if cached_entity and cached_entity.raw_profile:
                try:
                    raw = cached_entity.raw_profile
                    if entity_type == EntityType.COMPANY:
                        parsed_profile = CompanyIntelligenceProfile(**raw)
                    else:
                        parsed_profile = PersonIntelligenceProfile(**raw)
                    logger.info(f"Crustdata cache HIT for {identifier} (Entity ID: {cached_entity.id})")
                    return parsed_profile
                except Exception as err:
                    logger.warning(f"Cached entity {cached_entity.id} profile invalid ({err}); refreshing.")

        # 2. Check Credit Safety Threshold
        cost = CreditGuard.estimate_cost(level)
        CreditGuard.verify_budget_can_proceed(cost)

        # 3. Execute Enrichment via Client
        profile: Union[CompanyIntelligenceProfile, PersonIntelligenceProfile]
        if entity_type == EntityType.COMPANY:
            profile = await self.client.enrich_company(identifier, level=level)
        else:
            profile = await self.client.enrich_person(identifier, level=level)

        # 4. Persist in Database (Entity & Evidence)
        await self._persist_entity_and_evidence(db, profile, entity_type, level)

        return profile

    async def estimate_deep_enrichment_cost(
        self,
        identifier: str,
        entity_type: EntityType,
    ) -> DeepEnrichmentCostEstimate:
        """
        Returns estimated credit cost and current account balance before executing Level 3 Deep Enrichment.
        """
        credits_info = await self.client.get_account_credits()
        estimated_credits = CreditGuard.estimate_cost(EnrichmentLevel.LEVEL_3_DEEP)
        min_threshold = float(settings.CRUSTDATA_MIN_CREDIT_THRESHOLD)
        remaining = credits_info.remaining_credits

        can_proceed = (remaining - estimated_credits) >= min_threshold
        warning_msg = None
        if not can_proceed:
            warning_msg = (
                f"Insufficient credits for Level 3 Deep Enrichment: Requires {estimated_credits:.1f} credits, "
                f"but balance is {remaining:.1f} (min threshold {min_threshold:.1f})."
            )

        return DeepEnrichmentCostEstimate(
            entity_name=identifier,
            entity_type=entity_type,
            target_identifier=identifier,
            estimated_credits=estimated_credits,
            account_credits_available=remaining,
            safety_threshold=min_threshold,
            can_proceed=can_proceed,
            warning_message=warning_msg,
        )

    async def _find_cached_entity(
        self,
        db: AsyncSession,
        identifier: str,
        entity_type: EntityType,
    ) -> Optional[IntelligenceEntity]:
        """Finds fresh cached intelligence record within TTL."""
        ttl_cutoff = datetime.now(timezone.utc) - timedelta(days=settings.CRUSTDATA_CACHE_TTL_DAYS)

        stmt = select(IntelligenceEntity).where(
            and_(
                IntelligenceEntity.entity_type == entity_type.value,
                IntelligenceEntity.last_enriched_at >= ttl_cutoff,
                or_(
                    IntelligenceEntity.primary_name.ilike(f"%{identifier}%"),
                    IntelligenceEntity.primary_domain.ilike(f"%{identifier}%"),
                    IntelligenceEntity.profile_url.ilike(f"%{identifier}%"),
                ),
            )
        ).order_by(desc(IntelligenceEntity.last_enriched_at))

        res = await db.execute(stmt)
        return res.scalars().first()

    async def _persist_entity_and_evidence(
        self,
        db: AsyncSession,
        profile: Union[CompanyIntelligenceProfile, PersonIntelligenceProfile],
        entity_type: EntityType,
        level: EnrichmentLevel,
    ) -> IntelligenceEntity:
        """Saves or updates IntelligenceEntity and granular evidence provenance."""
        primary_name = profile.name if isinstance(profile, CompanyIntelligenceProfile) else profile.full_name
        primary_domain = profile.primary_domain if isinstance(profile, CompanyIntelligenceProfile) else None
        profile_url = (
            profile.linkedin_url
            if isinstance(profile, CompanyIntelligenceProfile)
            else profile.linkedin_url
        )

        # Check existing entity record to avoid duplicate rows
        existing_stmt = select(IntelligenceEntity).where(
            or_(
                IntelligenceEntity.id == profile.entity_id,
                and_(
                    IntelligenceEntity.primary_name == primary_name,
                    IntelligenceEntity.entity_type == entity_type.value,
                ),
                and_(
                    IntelligenceEntity.primary_domain == primary_domain,
                    IntelligenceEntity.primary_domain.isnot(None),
                ) if primary_domain else False,
            )
        )
        res = await db.execute(existing_stmt)
        entity = res.scalars().first()

        if not entity:
            entity = IntelligenceEntity(
                id=profile.entity_id,
                entity_type=entity_type.value,
                primary_name=primary_name,
                primary_domain=primary_domain,
                profile_url=profile_url,
                raw_profile=profile.model_dump(mode="json"),
                data_freshness=profile.data_freshness,
                enrichment_level=level.value,
                credits_consumed=profile.credits_consumed,
                is_mock=profile.is_mock,
                last_enriched_at=datetime.now(timezone.utc),
            )
            db.add(entity)
        else:
            # Sync returned profile entity_id with existing DB record id
            profile.entity_id = entity.id
            # Update existing record
            entity.raw_profile = profile.model_dump(mode="json")
            entity.data_freshness = profile.data_freshness
            entity.enrichment_level = level.value
            entity.credits_consumed += profile.credits_consumed
            entity.last_enriched_at = datetime.now(timezone.utc)

        await db.flush()

        # Persist granular evidence provenance
        for ev in profile.evidence:
            evidence_row = IntelligenceEvidence(
                id=str(uuid.uuid4()),
                entity_id=entity.id,
                data_category=ev.data_category,
                claim=ev.claim,
                source_url=ev.source_url,
                retrieval_timestamp=ev.retrieval_timestamp,
                confidence=ev.confidence,
                verification_classification=ev.verification_classification.value,
                original_source_metadata=ev.metadata,
            )
            db.add(evidence_row)

        await db.commit()
        return entity
