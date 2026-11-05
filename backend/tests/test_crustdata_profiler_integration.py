"""
Tests for Phase 6: Crustdata Integration with Existing Profiler Agent.
"""

import uuid
import pytest
from sqlalchemy import select

from app.db.session import init_db, AsyncSessionLocal
from app.agents.profiler.agent import ProfilerAgent
from app.agents.profiler.technology_profiler import TechnologyProfiler
from app.services.enrichment.company_search import CompanySearchService
from app.models.signal import Signal
from app.models.company import Company


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


def test_company_search_resolves_crustdata_entities():
    # 1. Existing known
    acme = CompanySearchService.lookup_firmographics("acme")
    assert acme is not None
    assert acme["domain"] == "acmecloud.io"

    # 2. Crustdata entities
    spacex = CompanySearchService.lookup_firmographics("SpaceX")
    assert spacex is not None
    assert spacex["name"] == "SpaceX"
    assert spacex["domain"] == "spacex.com"

    openai = CompanySearchService.lookup_firmographics("OpenAI")
    assert openai is not None
    assert openai["name"] == "OpenAI"
    assert openai["domain"] == "openai.com"


@pytest.mark.asyncio
async def test_technology_profiler_ingests_crustdata_technographics():
    profile = await TechnologyProfiler.profile_company(
        company_name="SpaceX",
        domain="spacex.com",
        raw_signal_text="Evaluating alternatives to Datadog for telemetry.",
    )
    assert profile.has_datadog_evidence is True
    # Verify Crustdata technographic evidence items present
    crust_ev = [e for e in profile.evidence if e.source == "CrustdataTechnographics"]
    assert len(crust_ev) > 0
    assert any(e.technology == "Kubernetes" for e in crust_ev)
    assert any(e.technology == "Grafana" for e in crust_ev)


@pytest.mark.asyncio
async def test_profiler_agent_populates_crustdata_decision_makers():
    sig_id = f"sig-test-{uuid.uuid4().hex[:6]}"
    async with AsyncSessionLocal() as db:
        sig = Signal(
            signal_id=sig_id,
            source="REDDIT",
            original_url=f"https://reddit.com/{sig_id}",
            vendor="Datadog",
            complaint_category="PRICING_SHOCK",
            raw_content="Our team at SpaceX (spacex.com) is dealing with massive Datadog custom metric overages.",
            urgency_score=0.95,
            status="NEW",
            extracted_evidence={"company_name": "SpaceX", "domain": "spacex.com"},
        )
        db.add(sig)
        await db.commit()

    agent = ProfilerAgent()
    async with AsyncSessionLocal() as db:
        summary = await agent.run_profiling_cycle(db, max_signals=1)
        assert summary.signals_processed == 1
        assert summary.companies_identified >= 1

        # Check saved Company record
        res = await db.execute(select(Company).where(Company.name == "SpaceX").order_by(Company.created_at.desc()))
        company = res.scalars().first()
        assert company is not None
        assert company.domain == "spacex.com"
        # Decision makers must be populated from Crustdata
        assert len(company.decision_makers) >= 1
        assert any("Elon Musk" in str(dm) for dm in company.decision_makers)
