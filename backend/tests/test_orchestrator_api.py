"""
API Tests for Central Orchestrator Endpoints.
Tests run, status, listing, metrics, retry endpoints, and human approval preservation.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.signal import Signal
from app.models.company import Company
from app.models.workflow import WorkflowExecution
from app.agents.orchestrator.state_machine import WorkflowState


@pytest.mark.asyncio
async def test_orchestrator_api_run_and_status():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Signal via API
        sig_id = f"test-sig-api-{uuid.uuid4().hex[:8]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "REDDIT",
            "original_url": "https://reddit.com/r/devops/comments/cost_runaway",
            "vendor": "Datadog",
            "complaint_category": "PRICING_SHOCK",
            "raw_content": "Our team at Nexus Payments (nexuspay.io) is looking to cut Datadog APM costs by 50% across 180 nodes.",
            "urgency_score": 0.90,
            "extracted_evidence": {"inferred_nodes": 180, "company_name": "Nexus Payments", "domain": "nexuspay.io"},
            "is_synthetic": True,
            "status": "NEW",
        })
        assert sig_res.status_code == 201
        signal_db_id = sig_res.json()["id"]

        # 1. Trigger Orchestrator Run
        run_res = await client.post("/api/v1/orchestrator/run", json={
            "signal_id": signal_db_id,
            "target_challenger": "SigNoz Cloud",
            "include_synthetic": True,
            "timeout_seconds": 30,
        })
        assert run_res.status_code == 200
        run_data = run_res.json()
        workflow_id = run_data["workflow_id"]
        assert run_data["status"] == "DRAFT_PENDING_APPROVAL"
        assert run_data["company_id"] is not None
        assert run_data["dossier_id"] is not None

        # 2. GET Workflow Status
        status_res = await client.get(f"/api/v1/orchestrator/status/{workflow_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["workflow_id"] == workflow_id
        assert len(status_data["step_history"]) >= 4

        # 3. GET Workflow List
        list_res = await client.get("/api/v1/orchestrator/workflows?limit=10")
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert list_data["total"] >= 1
        assert any(w["workflow_id"] == workflow_id for w in list_data["workflows"])

        # 4. GET Orchestrator Metrics
        metrics_res = await client.get("/api/v1/orchestrator/metrics")
        assert metrics_res.status_code == 200
        metrics_data = metrics_res.json()
        assert metrics_data["total_workflows"] >= 1
        assert metrics_data["pending_approval_count"] >= 1

        # 5. Non-existent workflow returns 404
        fake_res = await client.get(f"/api/v1/orchestrator/status/{uuid.uuid4()}")
        assert fake_res.status_code == 404


@pytest.mark.asyncio
async def test_orchestrator_api_retry_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a pre-failed workflow in DB
        async with AsyncSessionLocal() as db:
            signal = Signal(
                signal_id=f"test-sig-fail-{uuid.uuid4().hex[:8]}",
                source="REDDIT",
                original_url="https://test.com",
                complaint_category="PRICING_SHOCK",
                raw_content="Content",
                is_synthetic=True,
            )
            db.add(signal)
            await db.flush()

            company = Company(
                signal_id=signal.id,
                name="RetryCorp",
                domain="retrycorp.com",
                estimated_size="100-250 employees",
                icp_score=0.85,
                qualification_status="ACCEPTED",
                is_synthetic=True,
            )
            db.add(company)
            await db.flush()

            wf = WorkflowExecution(
                workflow_type="SINGLE_COMPANY",
                status=WorkflowState.FAILED.value,
                current_step="FINOPS",
                company_id=company.id,
                signal_id=signal.id,
                retry_count=1,
                max_retries=3,
                step_history=[
                    {"step_name": "PROFILER", "status": "SUCCESS", "started_at": "", "completed_at": "", "duration_ms": 50, "details": {}},
                    {"step_name": "QUALIFICATION", "status": "SUCCESS", "started_at": "", "completed_at": "", "duration_ms": 30, "details": {}},
                ],
                is_synthetic=True,
            )
            db.add(wf)
            await db.commit()
            wf_id = wf.id

        # Trigger Retry via API
        retry_res = await client.post(f"/api/v1/orchestrator/retry/{wf_id}")
        assert retry_res.status_code == 200
        retry_data = retry_res.json()
        assert retry_data["status"] == "DRAFT_PENDING_APPROVAL"
        assert retry_data["dossier_id"] is not None


@pytest.mark.asyncio
async def test_human_approval_gate_unbypassed_by_orchestrator():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Run orchestrator to completion
        sig_id = f"test-sig-gate-{uuid.uuid4().hex[:8]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "HACKER_NEWS",
            "original_url": "https://news.ycombinator.com/item?id=7777",
            "vendor": "Datadog",
            "complaint_category": "OUTAGE",
            "raw_content": "Our team at FinStream Cloud (finstream.io) suffered an outage from Datadog APM monitor lag.",
            "urgency_score": 0.85,
            "extracted_evidence": {"inferred_nodes": 200, "company_name": "FinStream Cloud", "domain": "finstream.io"},
            "is_synthetic": True,
            "status": "NEW",
        })
        assert sig_res.status_code == 201

        run_res = await client.post("/api/v1/orchestrator/run", json={
            "signal_id": sig_res.json()["id"],
            "target_challenger": "SigNoz Cloud",
            "timeout_seconds": 30,
        })
        assert run_res.status_code == 200
        dossier_id = run_res.json()["dossier_id"]

        # Ensure that Export is strictly BLOCKED (403 Forbidden) because status is DRAFT_PENDING_APPROVAL
        export_blocked = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_blocked.status_code == 403
        assert "Human approval is strictly required" in export_blocked.json()["detail"]

        # Human approves
        approve_res = await client.patch(f"/api/v1/copywriter/{dossier_id}/approve")
        assert approve_res.status_code == 200

        # Now export succeeds
        export_ok = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_ok.status_code == 200
        assert export_ok.json()["status"] == "EXPORTED"
