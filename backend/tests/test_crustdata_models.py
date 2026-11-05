"""
Tests for Phase 2: Database Models and Schemas.
"""

import uuid
import pytest
from sqlalchemy import select

from app.db.session import init_db, AsyncSessionLocal
from app.models.intelligence import (
    IntelligenceEntity,
    IntelligenceSearch,
    IntelligenceEvidence,
)


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.mark.asyncio
async def test_intelligence_entity_and_evidence_persistence():
    entity_id = str(uuid.uuid4())
    search_id = str(uuid.uuid4())
    evidence_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        # Create entity
        entity = IntelligenceEntity(
            id=entity_id,
            entity_type="COMPANY",
            primary_name="SpaceX",
            primary_domain="spacex.com",
            raw_profile={"entity_id": entity_id, "name": "SpaceX", "primary_domain": "spacex.com", "industry": "Aerospace"},
            data_freshness="CACHED",
            enrichment_level="LEVEL_2_STANDARD",
            credits_consumed=1.0,
            is_mock=True,
        )
        db.add(entity)

        # Create search log linked to entity
        search = IntelligenceSearch(
            id=search_id,
            search_query="SpaceX",
            entity_type="COMPANY",
            search_status="COMPLETED",
            selected_entity_id=entity_id,
            candidates=[{"name": "SpaceX", "domain": "spacex.com"}],
            credits_consumed=0.5,
            is_mock=True,
        )
        db.add(search)

        # Create evidence item
        evidence = IntelligenceEvidence(
            id=evidence_id,
            entity_id=entity_id,
            data_category="TECHNOGRAPHICS",
            claim="Installed software: Datadog (Observability)",
            source_url="https://spacex.com/careers",
            confidence=0.85,
            verification_classification="INFERRED",
            original_source_metadata={"snippet": "Experience with Datadog and Kubernetes required"},
        )
        db.add(evidence)

        await db.commit()

    # Query back
    async with AsyncSessionLocal() as db:
        res_e = await db.execute(select(IntelligenceEntity).where(IntelligenceEntity.id == entity_id))
        saved_entity = res_e.scalar_one()
        assert saved_entity.primary_name == "SpaceX"
        assert saved_entity.primary_domain == "spacex.com"
        assert saved_entity.is_mock is True

        res_ev = await db.execute(select(IntelligenceEvidence).where(IntelligenceEvidence.entity_id == entity_id))
        ev_items = res_ev.scalars().all()
        assert len(ev_items) == 1
        assert ev_items[0].verification_classification == "INFERRED"
        assert "Datadog" in ev_items[0].claim

        res_s = await db.execute(select(IntelligenceSearch).where(IntelligenceSearch.id == search_id))
        saved_search = res_s.scalar_one()
        assert saved_search.search_query == "SpaceX"
        assert saved_search.selected_entity_id == entity_id
