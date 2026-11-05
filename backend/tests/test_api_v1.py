"""
Integration Tests for Database & API v1 Endpoints (Phase 2).
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Ensure database tables are initialized before tests run."""
    await init_db()


@pytest.mark.asyncio
async def test_signal_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_sig_id = f"test-signal-{uuid.uuid4().hex[:8]}"
        signal_payload = {
            "signal_id": unique_sig_id,
            "source": "REDDIT",
            "original_url": f"https://reddit.com/r/devops/comments/{unique_sig_id}",
            "author_handle": "cloud_eng_lead",
            "vendor": "Datadog",
            "complaint_category": "PRICING_SHOCK",
            "raw_content": "Our Datadog APM and custom metrics bill jumped by 40% without warning.",
            "sentiment": "EXTREMELY_NEGATIVE",
            "urgency_score": 0.92,
            "extracted_evidence": {
                "reported_increase": "40%",
                "drivers": ["custom_metrics", "apm_hosts"],
            },
            "is_synthetic": True,
            "status": "NEW",
        }

        # 1. Create Signal
        create_res = await client.post("/api/v1/signals", json=signal_payload)
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["signal_id"] == unique_sig_id
        assert created["urgency_score"] == 0.92

        # 2. Prevent duplicate signals
        dup_res = await client.post("/api/v1/signals", json=signal_payload)
        assert dup_res.status_code == 409

        # 3. Read Signal by ID
        get_res = await client.get(f"/api/v1/signals/{created['id']}")
        assert get_res.status_code == 200
        assert get_res.json()["author_handle"] == "cloud_eng_lead"

        # 4. List Signals with filter
        list_res = await client.get("/api/v1/signals?source=REDDIT")
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_company_and_dossier_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        unique_sig_id = f"test-signal-{uuid.uuid4().hex[:8]}"
        # Create a parent signal first
        signal_payload = {
            "signal_id": unique_sig_id,
            "source": "HACKER_NEWS",
            "original_url": f"https://news.ycombinator.com/item?id={unique_sig_id}",
            "vendor": "Datadog",
            "complaint_category": "OUTAGE",
            "raw_content": "Datadog US1 outage took down our alert pipeline during deployment.",
            "urgency_score": 0.88,
            "is_synthetic": True,
        }
        sig_res = await client.post("/api/v1/signals", json=signal_payload)
        assert sig_res.status_code == 201
        signal_id = sig_res.json()["id"]

        # Create Company Profile
        company_payload = {
            "signal_id": signal_id,
            "name": f"Acme Cloud Infrastructure {unique_sig_id}",
            "domain": "acmecloud.io",
            "estimated_size": "100-250 employees",
            "industry": "Fintech / Payments",
            "tech_stack": {
                "observability": ["Datadog", "CloudWatch"],
                "cloud": ["AWS"],
                "containers": ["EKS", "Docker"],
            },
            "infrastructure_indicators": {
                "k8s_nodes": 120,
                "apm_services": 25,
            },
            "icp_score": 0.85,
            "identity_confidence": 0.90,
            "decision_makers": [
                {"role": "VP of Infrastructure", "confidence": 0.9},
                {"role": "Director of SRE", "confidence": 0.85},
            ],
            "evidence_sources": ["https://acmecloud.io/careers/sre-lead"],
            "is_synthetic": True,
        }
        comp_res = await client.post("/api/v1/companies", json=company_payload)
        assert comp_res.status_code == 201
        company_id = comp_res.json()["id"]

        # Create Deposition Dossier
        dossier_payload = {
            "signal_id": signal_id,
            "company_id": company_id,
            "financial_delta": {
                "datadog_monthly": 24000.0,
                "datadog_annual": 288000.0,
                "signoz_monthly": 6200.0,
                "signoz_annual": 74400.0,
                "estimated_migration_cost": 15000.0,
                "estimated_annual_savings": 213600.0,
                "payback_period_months": 0.85,
            },
            "migration_blueprint": {
                "proposed_architecture": "SigNoz Cloud via OpenTelemetry Collector",
                "collector_config_yaml": "receivers:\n  otlp:\n",
            },
            "outreach_drafts": {
                "email_subject": "Acme Cloud Datadog custom metric cost comparison vs OTel",
                "email_body": "Hi VP of Infrastructure, noticed the recent billing pain...",
                "status": "DRAFT_PENDING_APPROVAL",
            },
            "status": "DRAFT_PENDING_APPROVAL",
            "is_synthetic": True,
        }
        dos_res = await client.post("/api/v1/dossiers", json=dossier_payload)
        assert dos_res.status_code == 201
        dossier_id = dos_res.json()["id"]

        # Verify initial status is DRAFT_PENDING_APPROVAL
        assert dos_res.json()["status"] == "DRAFT_PENDING_APPROVAL"

        # Update status (Human-in-the-loop approval)
        status_update_res = await client.patch(
            f"/api/v1/dossiers/{dossier_id}/status",
            json={"status": "APPROVED"}
        )
        assert status_update_res.status_code == 200
        assert status_update_res.json()["status"] == "APPROVED"

        # Invalid status should return 400
        bad_status_res = await client.patch(
            f"/api/v1/dossiers/{dossier_id}/status",
            json={"status": "INVALID_STATE"}
        )
        assert bad_status_res.status_code == 400


@pytest.mark.asyncio
async def test_stats_and_logs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a test signal
        sig_id = f"test-signal-{uuid.uuid4().hex[:6]}"
        sig_res = await client.post("/api/v1/signals", json={
            "signal_id": sig_id,
            "source": "REDDIT",
            "original_url": f"https://reddit.com/{sig_id}",
            "vendor": "Datadog",
            "complaint_category": "PRICING_SHOCK",
            "raw_content": "Bill increase test",
            "is_synthetic": True,
        })
        assert sig_res.status_code == 201
        signal_db_id = sig_res.json()["id"]

        # Create a company with high ICP score (qualified prospect)
        comp_res = await client.post("/api/v1/companies", json={
            "signal_id": signal_db_id,
            "name": "Stats Test Corp",
            "icp_score": 0.85,
            "is_synthetic": True,
        })
        assert comp_res.status_code == 201
        company_db_id = comp_res.json()["id"]

        # Create a dossier with estimated savings
        dos_res = await client.post("/api/v1/dossiers", json={
            "signal_id": signal_db_id,
            "company_id": company_db_id,
            "financial_delta": {
                "estimated_annual_savings": 120000.0,
            },
            "is_synthetic": True,
        })
        assert dos_res.status_code == 201

        # Create execution log
        log_payload = {
            "agent_name": "LISTENER",
            "signal_id": sig_id,
            "status": "SUCCESS",
            "execution_time_ms": 320,
            "input_payload": {"query": "Datadog pricing"},
            "output_payload": {"signals_found": 3},
        }
        log_res = await client.post("/api/v1/logs", json=log_payload)
        assert log_res.status_code == 201

        # Check Overview Stats
        stats_res = await client.get("/api/v1/stats/overview")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["signals_detected"] >= 1
        assert stats["companies_identified"] >= 1
        assert stats["qualified_prospects"] >= 1
        assert stats["total_potential_annual_savings"] >= 120000.0
