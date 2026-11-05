"""
Tests for Phase 3: Generic Crustdata Intelligence Service.
"""

import pytest
from sqlalchemy import select, func, desc

from app.db.session import init_db, AsyncSessionLocal
from app.models.intelligence import (
    IntelligenceEntity,
    IntelligenceSearch,
    IntelligenceEvidence,
)
from app.services.crustdata.intelligence_service import CrustdataIntelligenceService
from app.services.crustdata.schemas import (
    EntityType,
    EnrichmentLevel,
    DeepEnrichmentCostEstimate,
    CompanyIntelligenceProfile,
    PersonIntelligenceProfile,
)


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


def test_entity_type_auto_detection():
    service = CrustdataIntelligenceService()

    # Company URLs
    assert service.detect_entity_type("https://www.linkedin.com/company/spacex") == EntityType.COMPANY
    assert service.detect_entity_type("https://openai.com") == EntityType.COMPANY
    assert service.detect_entity_type("spacex.com") == EntityType.COMPANY
    assert service.detect_entity_type("Datadog") == EntityType.COMPANY
    assert service.detect_entity_type("Apex Technologies Inc") == EntityType.COMPANY

    # Person URLs and Names
    assert service.detect_entity_type("https://www.linkedin.com/in/elonmusk") == EntityType.PERSON
    assert service.detect_entity_type("Elon Musk") == EntityType.PERSON
    assert service.detect_entity_type("Sam Altman") == EntityType.PERSON


@pytest.mark.asyncio
async def test_level_1_search_and_search_audit():
    service = CrustdataIntelligenceService()
    test_q = "SpaceX Falcon"

    async with AsyncSessionLocal() as db:
        res = await service.search_candidates(db, query=test_q, entity_type=EntityType.COMPANY)
        assert res.query == test_q
        assert res.detected_type == EntityType.COMPANY
        assert len(res.candidates) >= 1
        assert "SpaceX" in res.candidates[0].name

        # Verify audit record created in intelligence_searches
        stmt = (
            select(IntelligenceSearch)
            .where(IntelligenceSearch.search_query == test_q)
            .order_by(desc(IntelligenceSearch.created_at))
        )
        db_res = await db.execute(stmt)
        search_row = db_res.scalars().first()
        assert search_row is not None
        assert search_row.search_query == test_q
        assert search_row.entity_type == "COMPANY"


@pytest.mark.asyncio
async def test_level_2_standard_enrichment_and_caching():
    service = CrustdataIntelligenceService()

    async with AsyncSessionLocal() as db:
        # First call: Fetches and persists into DB
        profile = await service.enrich_entity(
            db,
            identifier="spacex.com",
            entity_type=EntityType.COMPANY,
            level=EnrichmentLevel.LEVEL_2_STANDARD,
            force_refresh=True,
        )
        assert isinstance(profile, CompanyIntelligenceProfile)
        assert profile.name == "SpaceX"
        assert profile.primary_domain == "spacex.com"
        assert len(profile.evidence) > 0

        # Verify DB has entity and evidence
        e_stmt = select(IntelligenceEntity).where(IntelligenceEntity.primary_domain == "spacex.com")
        entity_row = (await db.execute(e_stmt)).scalars().first()
        assert entity_row is not None
        assert entity_row.primary_name == "SpaceX"

        ev_stmt = select(func.count(IntelligenceEvidence.id)).where(IntelligenceEvidence.entity_id == entity_row.id)
        ev_count = (await db.execute(ev_stmt)).scalar()
        assert ev_count > 0

        # Second call: Cache HIT
        cached_profile = await service.enrich_entity(
            db,
            identifier="spacex.com",
            entity_type=EntityType.COMPANY,
            level=EnrichmentLevel.LEVEL_2_STANDARD,
            force_refresh=False,
        )
        assert isinstance(cached_profile, CompanyIntelligenceProfile)
        assert cached_profile.primary_domain == "spacex.com"


@pytest.mark.asyncio
async def test_level_3_deep_enrichment_confirmation_guard():
    service = CrustdataIntelligenceService()

    async with AsyncSessionLocal() as db:
        # Without confirmation: returns DeepEnrichmentCostEstimate
        unconfirmed = await service.enrich_entity(
            db,
            identifier="openai.com",
            entity_type=EntityType.COMPANY,
            level=EnrichmentLevel.LEVEL_3_DEEP,
            confirmation_confirmed=False,
        )
        assert isinstance(unconfirmed, DeepEnrichmentCostEstimate)
        assert unconfirmed.estimated_credits == 15.0
        assert unconfirmed.can_proceed is True

        # With confirmation: executes and returns full profile
        confirmed = await service.enrich_entity(
            db,
            identifier="openai.com",
            entity_type=EntityType.COMPANY,
            level=EnrichmentLevel.LEVEL_3_DEEP,
            confirmation_confirmed=True,
        )
        assert isinstance(confirmed, CompanyIntelligenceProfile)
        assert confirmed.name == "OpenAI"
        assert confirmed.enrichment_level == EnrichmentLevel.LEVEL_3_DEEP
        assert confirmed.data_freshness == "REALTIME_CRAWL"


@pytest.mark.asyncio
async def test_person_enrichment_and_provenance():
    service = CrustdataIntelligenceService()

    async with AsyncSessionLocal() as db:
        profile = await service.enrich_entity(
            db,
            identifier="Sam Altman",
            entity_type=EntityType.PERSON,
            level=EnrichmentLevel.LEVEL_2_STANDARD,
        )
        assert isinstance(profile, PersonIntelligenceProfile)
        assert profile.full_name == "Sam Altman"
        assert profile.is_decision_maker is True
        assert any(e.verification_classification.value == "VERIFIED" for e in profile.evidence)
