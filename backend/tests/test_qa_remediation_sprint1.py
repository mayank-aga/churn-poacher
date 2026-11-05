"""
Regression Tests for QA Remediation Sprint 1.
Verifies fixes for BUG-04, BUG-05, BUG-06, BUG-09, and SUS-02.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import init_db, AsyncSessionLocal
from app.models.signal import Signal
from app.models.company import Company
from app.models.dossier import DepositionDossier
from app.services.sources.synthetic_generator import SyntheticSignalGenerator
from app.agents.profiler.entity_resolver import EntityResolver


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Ensure database tables are initialized before tests run."""
    await init_db()


# ============================================================================
# TASK 2 (BUG-04): Dossiers Filtering Tests
# ============================================================================
@pytest.mark.asyncio
async def test_dossiers_filtering_by_company_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create two distinct test companies
        comp_a_id = str(uuid.uuid4())
        comp_b_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as db:
            db.add(Company(id=comp_a_id, signal_id=str(uuid.uuid4()), name="Company Alpha", domain="alpha.test", qualification_status="ACCEPTED"))
            db.add(Company(id=comp_b_id, signal_id=str(uuid.uuid4()), name="Company Beta", domain="beta.test", qualification_status="ACCEPTED"))
            
            dossier_a = DepositionDossier(
                id=str(uuid.uuid4()),
                company_id=comp_a_id,
                signal_id=str(uuid.uuid4()),
                status="DRAFT_PENDING_APPROVAL",
                financial_delta={"estimated_annual_savings": 120000.0},
            )
            dossier_b = DepositionDossier(
                id=str(uuid.uuid4()),
                company_id=comp_b_id,
                signal_id=str(uuid.uuid4()),
                status="APPROVED",
                financial_delta={"estimated_annual_savings": 85000.0},
            )
            db.add(dossier_a)
            db.add(dossier_b)
            await db.commit()

        # 1. No filter: returns dossiers from multiple companies
        res_all = await client.get("/api/v1/dossiers")
        assert res_all.status_code == 200
        all_dossiers = res_all.json()
        assert any(d["company_id"] == comp_a_id for d in all_dossiers)
        assert any(d["company_id"] == comp_b_id for d in all_dossiers)

        # 2. Filter by valid company A
        res_a = await client.get(f"/api/v1/dossiers?company_id={comp_a_id}")
        assert res_a.status_code == 200
        dossiers_a = res_a.json()
        assert len(dossiers_a) >= 1
        assert all(d["company_id"] == comp_a_id for d in dossiers_a)

        # 3. Filter by valid company B
        res_b = await client.get(f"/api/v1/dossiers?company_id={comp_b_id}")
        assert res_b.status_code == 200
        dossiers_b = res_b.json()
        assert len(dossiers_b) >= 1
        assert all(d["company_id"] == comp_b_id for d in dossiers_b)

        # 4. Company ID with no dossiers
        unused_comp_id = str(uuid.uuid4())
        res_empty = await client.get(f"/api/v1/dossiers?company_id={unused_comp_id}")
        assert res_empty.status_code == 200
        assert res_empty.json() == []

        # 5. Invalid / arbitrary string format
        res_invalid = await client.get("/api/v1/dossiers?company_id=non-existent-company-xyz")
        assert res_invalid.status_code == 200
        assert res_invalid.json() == []


# ============================================================================
# TASK 3 (BUG-05): Companies Filtering Tests
# ============================================================================
@pytest.mark.asyncio
async def test_companies_filtering_by_qualification_status():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_suffix = uuid.uuid4().hex[:6]
        c_accepted_id = str(uuid.uuid4())
        c_rejected_id = str(uuid.uuid4())
        c_review_id = str(uuid.uuid4())

        async with AsyncSessionLocal() as db:
            db.add(Company(id=c_accepted_id, signal_id=str(uuid.uuid4()), name=f"Accepted Co {unique_suffix}", domain=f"acc-{unique_suffix}.io", qualification_status="ACCEPTED", icp_score=0.88))
            db.add(Company(id=c_rejected_id, signal_id=str(uuid.uuid4()), name=f"Rejected Co {unique_suffix}", domain=f"rej-{unique_suffix}.io", qualification_status="REJECTED", icp_score=0.30))
            db.add(Company(id=c_review_id, signal_id=str(uuid.uuid4()), name=f"Review Co {unique_suffix}", domain=f"rev-{unique_suffix}.io", qualification_status="REVIEW_REQUIRED", icp_score=0.65))
            await db.commit()

        # 1. Filter ACCEPTED
        res_acc = await client.get("/api/v1/companies?qualification_status=ACCEPTED")
        assert res_acc.status_code == 200
        acc_list = res_acc.json()
        assert any(c["id"] == c_accepted_id for c in acc_list)
        assert all(c["qualification_status"] == "ACCEPTED" for c in acc_list)

        # 2. Filter REJECTED
        res_rej = await client.get("/api/v1/companies?qualification_status=REJECTED")
        assert res_rej.status_code == 200
        rej_list = res_rej.json()
        assert any(c["id"] == c_rejected_id for c in rej_list)
        assert all(c["qualification_status"] == "REJECTED" for c in rej_list)

        # 3. Filter REVIEW_REQUIRED
        res_rev = await client.get("/api/v1/companies?qualification_status=REVIEW_REQUIRED")
        assert res_rev.status_code == 200
        rev_list = res_rev.json()
        assert any(c["id"] == c_review_id for c in rev_list)
        assert all(c["qualification_status"] == "REVIEW_REQUIRED" for c in rev_list)


# ============================================================================
# TASK 4 (BUG-06): Signals Filtering Tests
# ============================================================================
@pytest.mark.asyncio
async def test_signals_filtering_by_category_and_urgency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_sig1 = f"sig-price-{uuid.uuid4().hex[:6]}"
        unique_sig2 = f"sig-outage-{uuid.uuid4().hex[:6]}"
        unique_sig3 = f"sig-low-urgency-{uuid.uuid4().hex[:6]}"

        async with AsyncSessionLocal() as db:
            db.add(Signal(
                signal_id=unique_sig1,
                source="REDDIT",
                original_url=f"https://reddit.com/{unique_sig1}",
                vendor="Datadog",
                complaint_category="PRICING_SHOCK",
                raw_content="Massive Datadog price spike on custom metrics.",
                urgency_score=0.95,
                status="NEW",
            ))
            db.add(Signal(
                signal_id=unique_sig2,
                source="HACKER_NEWS",
                original_url=f"https://news.ycombinator.com/{unique_sig2}",
                vendor="Datadog",
                complaint_category="OUTAGE",
                raw_content="Datadog US1 outage in progress.",
                urgency_score=0.89,
                status="NEW",
            ))
            db.add(Signal(
                signal_id=unique_sig3,
                source="REDDIT",
                original_url=f"https://reddit.com/{unique_sig3}",
                vendor="Datadog",
                complaint_category="PRICING_SHOCK",
                raw_content="Minor question about Datadog billing tiers.",
                urgency_score=0.45,
                status="NEW",
            ))
            await db.commit()

        # 1. Filter by complaint_category
        res_cat = await client.get("/api/v1/signals?complaint_category=OUTAGE")
        assert res_cat.status_code == 200
        outage_signals = res_cat.json()
        assert any(s["signal_id"] == unique_sig2 for s in outage_signals)
        assert all(s["complaint_category"] == "OUTAGE" for s in outage_signals)

        # 2. Filter by min_urgency
        res_urg = await client.get("/api/v1/signals?min_urgency=0.85")
        assert res_urg.status_code == 200
        urgent_signals = res_urg.json()
        assert any(s["signal_id"] == unique_sig1 for s in urgent_signals)
        assert any(s["signal_id"] == unique_sig2 for s in urgent_signals)
        assert not any(s["signal_id"] == unique_sig3 for s in urgent_signals)
        assert all(s["urgency_score"] >= 0.85 for s in urgent_signals)

        # 3. Combined source, category, and min_urgency
        res_comb = await client.get("/api/v1/signals?source=REDDIT&complaint_category=PRICING_SHOCK&min_urgency=0.90")
        assert res_comb.status_code == 200
        comb_signals = res_comb.json()
        assert any(s["signal_id"] == unique_sig1 for s in comb_signals)
        assert not any(s["signal_id"] == unique_sig3 for s in comb_signals)
        assert all(s["source"] == "REDDIT" and s["complaint_category"] == "PRICING_SHOCK" and s["urgency_score"] >= 0.90 for s in comb_signals)


# ============================================================================
# TASK 5 (BUG-09): Correct Dossiers Count in Overview Stats
# ============================================================================
@pytest.mark.asyncio
async def test_stats_overview_correct_dossier_count():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Pre-check stats
        res_initial = await client.get("/api/v1/stats/overview")
        assert res_initial.status_code == 200
        initial_stats = res_initial.json()
        initial_dossiers = initial_stats.get("dossiers_count", 0)

        # Insert a company with qualified ICP score, but NO dossier
        comp_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as db:
            db.add(Company(id=comp_id, signal_id=str(uuid.uuid4()), name="Stats Test Co", domain="statstest.io", qualification_status="ACCEPTED", icp_score=0.95))
            await db.commit()

        res_after_company = await client.get("/api/v1/stats/overview")
        stats_after_comp = res_after_company.json()
        # Qualified prospects incremented, but dossiers_count must remain unchanged
        assert stats_after_comp["dossiers_count"] == initial_dossiers
        assert stats_after_comp["qualified_prospects"] >= 1

        # Now insert a real DepositionDossier
        dossier_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as db:
            db.add(DepositionDossier(
                id=dossier_id,
                company_id=comp_id,
                signal_id=str(uuid.uuid4()),
                status="DRAFT_PENDING_APPROVAL",
                financial_delta={"estimated_annual_savings": 45000.0},
            ))
            await db.commit()

        res_final = await client.get("/api/v1/stats/overview")
        stats_final = res_final.json()
        # Dossiers count must increment by exactly 1
        assert stats_final["dossiers_count"] == initial_dossiers + 1
        assert stats_final["total_potential_annual_savings"] >= 45000.0


# ============================================================================
# TASK 6 (SUS-02): Synthetic Data & Entity Resolution Tests
# ============================================================================
def test_synthetic_scenarios_entity_resolution_and_provenance():
    signals = SyntheticSignalGenerator.generate_signals(count=4)
    assert len(signals) == 4

    # 1. All generated synthetic data must have is_synthetic=True
    for s in signals:
        assert s.is_synthetic is True, f"Signal {s.source_id} failed synthetic labeling"
        assert "demo.churnpoacher.io" in s.source_url

    # 2. Scenario 1 (CloudScale Dynamics): Explicit affiliation must resolve
    sig_cloudscale = next(s for s in signals if s.source_id == "synth-dd-pricing-001")
    cand_1, ev_1 = EntityResolver.resolve(
        title=sig_cloudscale.title or "",
        content=sig_cloudscale.content,
        author=sig_cloudscale.author,
        source_url=sig_cloudscale.source_url,
        extracted_evidence=sig_cloudscale.extracted_evidence,
    )
    assert cand_1 is not None, "Explicit synthetic affiliation with CloudScale Dynamics failed to resolve"
    assert cand_1.company_name == "CloudScale Dynamics"
    assert cand_1.domain == "cloudscaledynamics.io"
    assert cand_1.identity_confidence >= 0.80

    # 3. Scenario 3 (ApexFin Technologies): Explicit affiliation must resolve
    sig_apexfin = next(s for s in signals if s.source_id == "synth-dd-migration-003")
    cand_3, ev_3 = EntityResolver.resolve(
        title=sig_apexfin.title or "",
        content=sig_apexfin.content,
        author=sig_apexfin.author,
        source_url=sig_apexfin.source_url,
        extracted_evidence=sig_apexfin.extracted_evidence,
    )
    assert cand_3 is not None, "Explicit synthetic affiliation with ApexFin Technologies failed to resolve"
    assert cand_3.company_name == "ApexFin Technologies"
    assert cand_3.domain == "apexfintech.io"
    assert cand_3.identity_confidence >= 0.80

    # 4. Scenario 2 (Anonymous Outage Vent): Must remain UNRESOLVED (Anti-Hallucination Guardrail)
    sig_anon = next(s for s in signals if s.source_id == "synth-dd-outage-002")
    cand_2, ev_2 = EntityResolver.resolve(
        title=sig_anon.title or "",
        content=sig_anon.content,
        author=sig_anon.author,
        source_url=sig_anon.source_url,
        extracted_evidence=sig_anon.extracted_evidence,
    )
    assert cand_2 is None, "Anonymous outage signal must NOT hallucinate a corporate entity"
