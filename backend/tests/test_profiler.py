"""
Integration Tests for Profiler Agent and Profiler API endpoints.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db, AsyncSessionLocal
from app.models.signal import Signal
from app.models.company import Company
from app.agents.profiler.agent import ProfilerAgent


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.mark.asyncio
async def test_profiler_agent_end_to_end_batch():
    async with AsyncSessionLocal() as session:
        agent = ProfilerAgent()

        # 1. Insert a resolvable signal (explicit company declaration)
        resolvable_sig = Signal(
            signal_id=f"sig-prof-{uuid.uuid4().hex[:6]}",
            source="REDDIT",
            original_url="https://acmecloud.io/blog/scaling",
            author_handle="u/acme_vp_eng",
            vendor="Datadog",
            complaint_category="PRICING_SHOCK",
            raw_content="Our team at Acme Cloud Infrastructure has 120 nodes on Kubernetes and our Datadog APM bill exploded.",
            urgency_score=0.92,
            extracted_evidence={"inferred_nodes": 120, "products_mentioned": ["apm", "custom metrics"]},
            status="NEW",
            is_synthetic=True,
        )
        session.add(resolvable_sig)

        # 2. Insert an anonymous unresolvable signal
        anon_sig = Signal(
            signal_id=f"sig-anon-{uuid.uuid4().hex[:6]}",
            source="HACKER_NEWS",
            original_url="https://news.ycombinator.com/item?id=777123",
            author_handle="throwaway_user",
            vendor="Datadog",
            complaint_category="OUTAGE",
            raw_content="Datadog is down again today. Anyone else?",
            urgency_score=0.85,
            status="NEW",
            is_synthetic=True,
        )
        session.add(anon_sig)
        await session.commit()

        # 3. Run Profiler Cycle
        summary = await agent.run_profiling_cycle(db=session, max_signals=10)

        assert summary.signals_processed >= 2
        assert summary.companies_identified >= 1
        assert summary.unresolved_signals >= 1

        # Check Signal statuses updated
        await session.refresh(resolvable_sig)
        await session.refresh(anon_sig)
        assert resolvable_sig.status in ["QUALIFIED", "PROFILED"]
        assert anon_sig.status == "UNRESOLVED"


@pytest.mark.asyncio
async def test_profiler_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a new signal first
        sig_id = f"test-prof-api-{uuid.uuid4().hex[:6]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "REDDIT",
            "original_url": "https://acmecloud.io/careers/sre",
            "vendor": "Datadog",
            "complaint_category": "MIGRATION_INTENT",
            "raw_content": "We at Acme Cloud Infrastructure are migrating from Datadog to SigNoz with OpenTelemetry.",
            "urgency_score": 0.90,
            "status": "NEW",
            "is_synthetic": True,
        })
        assert sig_res.status_code == 201

        # 1. Trigger Profiler Run via API
        run_res = await client.post("/api/v1/profiler/run", json={"max_signals": 5})
        assert run_res.status_code == 200
        summary = run_res.json()
        assert summary["signals_processed"] >= 1
        assert summary["companies_identified"] >= 1

        # 2. Check Profiler Status
        status_res = await client.get("/api/v1/profiler/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["total_companies_profiled"] >= 1

        # 3. List Companies
        list_res = await client.get("/api/v1/profiler/companies")
        assert list_res.status_code == 200
        companies = list_res.json()
        assert len(companies) >= 1
        company_id = companies[0]["id"]
        assert "qualification_status" in companies[0]
        assert "evidence_records" in companies[0]

        # 4. Get Company Intelligence by ID
        get_res = await client.get(f"/api/v1/profiler/companies/{company_id}")
        assert get_res.status_code == 200
        company = get_res.json()
        assert company["name"] != ""
        assert company["icp_score"] >= 0.0
        assert company["identity_confidence"] >= 0.0

        # 5. Check Profiler Metrics
        metrics_res = await client.get("/api/v1/profiler/metrics")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        assert metrics["companies_identified"] >= 1
        assert "average_icp_score" in metrics
        assert "average_identity_confidence" in metrics
