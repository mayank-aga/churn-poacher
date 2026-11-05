"""
Integration Tests for FinOps, Architecture Agent, and Deposition Dossier API endpoints.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.mark.asyncio
async def test_finops_and_architecture_dossier_integration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create a parent signal
        sig_id = f"test-fin-sig-{uuid.uuid4().hex[:6]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "REDDIT",
            "original_url": "https://acmecloud.io/blog/scaling",
            "vendor": "Datadog",
            "complaint_category": "PRICING_SHOCK",
            "raw_content": "Our Datadog bill increased by 40%.",
            "urgency_score": 0.90,
            "extracted_evidence": {"inferred_nodes": 120},
            "status": "QUALIFIED",
            "is_synthetic": True,
        })
        assert sig_res.status_code == 201
        signal_db_id = sig_res.json()["id"]

        # 2. Create Company
        comp_res = await client.post("/api/v1/companies", json={
            "signal_id": signal_db_id,
            "name": "Acme Cloud Infrastructure",
            "domain": "acmecloud.io",
            "estimated_size": "100-250 employees",
            "infrastructure_indicators": {"k8s_nodes": 120},
            "icp_score": 0.85,
            "identity_confidence": 0.90,
            "qualification_status": "ACCEPTED",
            "is_synthetic": True,
        })
        assert comp_res.status_code == 201
        company_id = comp_res.json()["id"]

        # 3. Test POST /api/v1/finops/run/{company_id}
        fin_run_res = await client.post(f"/api/v1/finops/run/{company_id}")
        assert fin_run_res.status_code == 200
        fin_data = fin_run_res.json()
        assert "scenarios" in fin_data
        assert "BASE" in fin_data["scenarios"]
        assert fin_data["scenarios"]["BASE"]["signoz_cloud_annual_savings"] > 0

        # 4. Test POST /api/v1/architecture/run/{company_id}
        arch_run_res = await client.post(f"/api/v1/architecture/run/{company_id}?target_backend=SigNoz Cloud")
        assert arch_run_res.status_code == 200
        arch_data = arch_run_res.json()
        assert "collector_config_yaml" in arch_data
        assert "phases" in arch_data
        assert len(arch_data["phases"]) == 7

        # 5. Test POST /api/v1/finops/dossier/{company_id} (Dossier Persistence)
        dossier_res = await client.post(f"/api/v1/finops/dossier/{company_id}")
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()
        assert dossier["company_id"] == company_id
        assert dossier["status"] == "DRAFT_PENDING_APPROVAL"
        assert "financial_delta" in dossier
        assert "migration_blueprint" in dossier
        assert dossier["financial_delta"]["estimated_annual_savings"] > 0

        # 6. Test GET /api/v1/finops/{company_id}
        get_fin_res = await client.get(f"/api/v1/finops/{company_id}")
        assert get_fin_res.status_code == 200
        assert get_fin_res.json()["company_name"] == "Acme Cloud Infrastructure"

        # 7. Test GET /api/v1/architecture/{company_id}
        get_arch_res = await client.get(f"/api/v1/architecture/{company_id}")
        assert get_arch_res.status_code == 200
        assert "phases" in get_arch_res.json()

        # 8. Test GET /api/v1/finops/pricing
        pricing_res = await client.get("/api/v1/finops/pricing")
        assert pricing_res.status_code == 200
        assert len(pricing_res.json()) >= 10

        # 9. Test GET /api/v1/finops/metrics
        metrics_res = await client.get("/api/v1/finops/metrics")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        assert metrics["dossiers_generated"] >= 1
        assert metrics["total_potential_annual_savings_usd"] > 0
