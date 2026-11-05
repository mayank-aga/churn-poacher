"""
End-to-End Tests for Copywriter Agent and Human-in-the-Loop Governance API.
Tests generation, persistence, approval, rejection, and strictly gated export.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.models.signal import Signal
from app.models.dossier import DepositionDossier
from app.agents.copywriter.agent import CopywriterAgent


@pytest.mark.asyncio
async def test_copywriter_agent_run_and_persist():
    async with AsyncSessionLocal() as db_session:
        # Setup Signal
        signal = Signal(
            signal_id=f"test-sig-{uuid.uuid4().hex[:8]}",
            source="REDDIT",
            original_url="https://reddit.com/r/devops/comments/pricing_shock",
            complaint_category="PRICING_SHOCK",
            raw_content="Datadog bill increased by 60% after switching to EKS",
            urgency_score=0.85,
            is_synthetic=True,
        )
        db_session.add(signal)
        await db_session.flush()

        # Setup Company
        company = Company(
            signal_id=signal.id,
            name="OmniCloud Platform",
            domain="omnicloud.dev",
            industry="Cloud Infrastructure",
            estimated_size="100-500 employees",
            icp_score=0.88,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db_session.add(company)
        await db_session.flush()

        # Setup pre-existing FinOps/Architecture Dossier
        dossier = DepositionDossier(
            company_id=company.id,
            signal_id=signal.id,
            financial_delta={
                "estimated_annual_savings": 88000.0,
                "scenarios": {
                    "BASE": {
                        "current_datadog_annual": 130000.0,
                        "signoz_cloud_annual": 42000.0,
                        "signoz_cloud_annual_savings": 88000.0,
                        "signoz_cloud_savings_pct": 68.0,
                        "payback_period_months": 1.6,
                    }
                },
            },
            migration_blueprint={
                "proposed_target_architecture": "SigNoz Cloud via OTel Collector",
            },
            status="DRAFT_PENDING_APPROVAL",
            is_synthetic=True,
        )
        db_session.add(dossier)
        await db_session.commit()

        # Run Copywriter
        result = await CopywriterAgent.run_and_persist(
            company_id=company.id,
            target_challenger="SigNoz Cloud",
            db=db_session,
        )

        assert result["status"] == "DRAFT_PENDING_APPROVAL"
        package = result["outreach_package"]
        assert package["company_name"] == "OmniCloud Platform"
        assert len(package["executive_emails"]) == 2
        assert package["linkedin_sequence"]["step_1_connection_request"] is not None
        assert package["technical_pitch"]["zero_code_migration_path"] is not None
        assert package["value_proposition"]["annual_savings_usd"] == 88000.0
        assert len(package["objection_matrix"]["items"]) == 7
        assert package["evidence_audit"]["passed"] is True


@pytest.mark.asyncio
async def test_copywriter_api_endpoints_and_governance():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Setup Signal via API
        sig_id = f"test-sig-{uuid.uuid4().hex[:8]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "HACKER_NEWS",
            "original_url": "https://news.ycombinator.com/item?id=99999",
            "vendor": "Datadog",
            "complaint_category": "OUTAGE",
            "raw_content": "Datadog latency monitor outage during prime trading hours",
            "urgency_score": 0.9,
            "is_synthetic": True,
            "status": "QUALIFIED",
        })
        assert sig_res.status_code == 201
        signal_db_id = sig_res.json()["id"]

        # Setup Company via API
        comp_res = await client.post("/api/v1/companies", json={
            "signal_id": signal_db_id,
            "name": "CryptoLedger Inc",
            "domain": "cryptoledger.com",
            "industry": "Fintech",
            "estimated_size": "50-250 employees",
            "icp_score": 0.82,
            "identity_confidence": 0.90,
            "qualification_status": "ACCEPTED",
            "is_synthetic": True,
        })
        assert comp_res.status_code == 201
        company_id = comp_res.json()["id"]

        # 1. Metrics Endpoint
        metrics_res = await client.get("/api/v1/copywriter/metrics")
        assert metrics_res.status_code == 200
        metrics_data = metrics_res.json()
        assert "pending_human_approval" in metrics_data
        assert "governance_rule" in metrics_data

        # 2. Run Copywriter via API
        run_res = await client.post(f"/api/v1/copywriter/run/{company_id}?target_challenger=SigNoz Cloud")
        assert run_res.status_code == 200
        run_data = run_res.json()
        dossier_id = run_data["dossier_id"]
        assert run_data["status"] == "DRAFT_PENDING_APPROVAL"

        # 3. GET drafts for company
        get_res = await client.get(f"/api/v1/copywriter/{company_id}")
        assert get_res.status_code == 200
        assert get_res.json()["company_id"] == company_id

        # 4. Gated Export: Attempting export BEFORE approval MUST FAIL with 403 Forbidden!
        export_blocked_res = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_blocked_res.status_code == 403
        assert "Export blocked" in export_blocked_res.json()["detail"]

        # 5. Human Approval
        approve_res = await client.patch(f"/api/v1/copywriter/{dossier_id}/approve")
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "APPROVED"

        # 6. Gated Export: Attempting export AFTER approval MUST SUCCEED with 200 OK!
        export_success_res = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_success_res.status_code == 200
        export_data = export_success_res.json()
        assert export_data["status"] == "EXPORTED"
        assert export_data["company_name"] == "CryptoLedger Inc"
        assert len(export_data["markdown_bundle"]) > 500
        assert "Executive Emails" in export_data["markdown_bundle"]

        # 7. Rejection Endpoint
        reject_res = await client.patch(
            f"/api/v1/copywriter/{dossier_id}/reject",
            json={"reason": "Revise tone for enterprise compliance team"},
        )
        assert reject_res.status_code == 200
        assert reject_res.json()["status"] == "REJECTED"
