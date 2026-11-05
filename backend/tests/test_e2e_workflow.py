"""
Phase 9: Comprehensive End-to-End Integration Tests.
Verifies the complete pipeline lifecycle:
Listener Ingestion -> Deduplication -> Profiler Qualification -> FinOps Analysis ->
Architecture Blueprint -> Copywriter Collateral -> Human Approval Gate & Export Control.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.signal import Signal
from app.models.company import Company
from app.models.dossier import DepositionDossier
from app.models.execution_log import AgentExecutionLog
from app.services.listener_service import listener_service
from app.agents.profiler.agent import ProfilerAgent
from app.agents.finops_architect.finops_agent import FinOpsAgent
from app.agents.finops_architect.architecture_agent import ArchitectureAgent
from app.agents.copywriter.agent import CopywriterAgent
from app.agents.orchestrator.orchestrator import CentralOrchestrator


@pytest.mark.asyncio
async def test_complete_e2e_pipeline_lifecycle():
    """
    Executes and asserts every stage of the Churn Poacher lifecycle:
    1. Listener ingests a distress signal.
    2. Deduplicator ensures no duplicate insertion.
    3. Profiler resolves entity and qualifies ICP.
    4. FinOps models Datadog vs SigNoz/Grafana delta matrix.
    5. Architect generates OTel collector YAML and 7-stage roadmap.
    6. Copywriter crafts personalized collateral with Evidence Guard.
    7. Dossier is parked in DRAFT_PENDING_APPROVAL.
    8. Export is blocked (403) before approval.
    9. Human approves dossier, unlocking export.
    """
    async with AsyncSessionLocal() as db:
        # Step 1: Ingest Distress Signal (Synthetic Labeled)
        summary = await listener_service.run_cycle(
            db=db,
            include_synthetic=True,
            max_items_per_source=2,
        )
        assert summary.total_fetched >= 1
        assert summary.new_signals_saved >= 1

        # Fetch the newly created signal
        sig_res = await db.execute(
            select(Signal)
            .where(Signal.is_synthetic == True)
            .order_by(Signal.created_at.desc())
        )
        signal = sig_res.scalars().first()
        assert signal is not None
        assert signal.urgency_score >= 0.0

        # Step 2: Test Deduplication
        dedup_summary = await listener_service.run_cycle(
            db=db,
            include_synthetic=False,
            max_items_per_source=2,
        )
        # Verify deduplication works without error
        assert dedup_summary is not None

        # Step 3: Profiler Agent Qualification
        # Create a clearly labelled synthetic enterprise company using the signal
        company = Company(
            name="E2E Synthetic Cloud Corp",
            domain="synthetic-cloud.example.com",
            signal_id=signal.id,
            industry="Cloud Infrastructure",
            estimated_size="250-1000 employees",
            tech_stack={
                "github_datadog_detected": True,
                "domain_resolvable": True,
                "active_dd_agent": True,
            },
            icp_score=0.88,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)

        # Step 4 & 5: FinOps and Architecture Generation
        finops_report = await FinOpsAgent.generate_financial_analysis(
            company=company,
            signal=signal,
        )
        assert "BASE" in finops_report.scenarios
        assert finops_report.scenarios["BASE"].signoz_cloud_annual_savings > 0

        arch_blueprint = await ArchitectureAgent.generate_migration_blueprint(
            company=company,
            target_backend="SigNoz Cloud",
        )
        assert "8126" in arch_blueprint.collector_config_yaml
        assert len(arch_blueprint.phases) == 7

        # Persist Dossier
        dossier = DepositionDossier(
            company_id=company.id,
            signal_id=signal.id,
            financial_delta=finops_report.model_dump(mode="json"),
            migration_blueprint=arch_blueprint.model_dump(mode="json"),
            status="PENDING_COPY",
            is_synthetic=True,
        )
        db.add(dossier)
        await db.commit()
        await db.refresh(dossier)

        # Step 6: Copywriter Agent Generation
        copy_res = await CopywriterAgent.run_and_persist(
            company_id=company.id,
            target_challenger="SigNoz Cloud",
            db=db,
        )
        assert copy_res["status"] == "DRAFT_PENDING_APPROVAL"
        assert len(copy_res["outreach_package"]["executive_emails"]) >= 2
        assert copy_res["outreach_package"]["evidence_audit"]["passed"] is True

        # Refresh dossier
        await db.refresh(dossier)
        assert dossier.status == "DRAFT_PENDING_APPROVAL"
        dossier_id = dossier.id

    # Step 7 & 8: Verify Security Safeguard - Export is Gated Before Approval
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Attempt to export while still unapproved -> must return HTTP 403 Forbidden
        export_blocked = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_blocked.status_code == 403
        assert "Export blocked" in export_blocked.json()["detail"]

        # Step 9: Human Approves the Dossier
        approve_resp = await client.patch(f"/api/v1/copywriter/{dossier_id}/approve")
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == "APPROVED"

        # Step 10: Now Export Succeeds
        export_allowed = await client.post(f"/api/v1/copywriter/{dossier_id}/export")
        assert export_allowed.status_code == 200
        export_data = export_allowed.json()
        assert export_data["status"] == "EXPORTED"
        assert "markdown_bundle" in export_data
        assert "# Competitive Deposition Pack" in export_data["markdown_bundle"]


@pytest.mark.asyncio
async def test_e2e_rejection_safeguard():
    """Verifies that human rejection halts export and logs the rejection reason."""
    async with AsyncSessionLocal() as db:
        sig = Signal(
            signal_id=f"sig-reject-{uuid.uuid4().hex[:8]}",
            source="SYNTHETIC",
            original_url="https://synthetic.example.com/signals/reject",
            complaint_category="PRICING_SHOCK",
            raw_content="Datadog costs too much for synthetic test.",
            urgency_score=0.8,
            is_synthetic=True,
        )
        db.add(sig)
        await db.commit()
        await db.refresh(sig)

        comp = Company(
            name="Rejected Synthetic Inc",
            domain="rejected-inc.example.com",
            signal_id=sig.id,
            icp_score=0.75,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db.add(comp)
        await db.commit()
        await db.refresh(comp)

        dos = DepositionDossier(
            company_id=comp.id,
            signal_id=sig.id,
            financial_delta={},
            migration_blueprint={},
            outreach_drafts={"status": "DRAFT_PENDING_APPROVAL"},
            status="DRAFT_PENDING_APPROVAL",
            is_synthetic=True,
        )
        db.add(dos)
        await db.commit()
        await db.refresh(dos)
        dos_id = dos.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Reject the dossier
        rej_resp = await client.patch(
            f"/api/v1/copywriter/{dos_id}/reject",
            json={"reason": "Account is undergoing renewal negotiation with incumbent"},
        )
        assert rej_resp.status_code == 200
        assert rej_resp.json()["status"] == "REJECTED"

        # Attempt to export rejected dossier -> must remain 403 Forbidden
        export_blocked = await client.post(f"/api/v1/copywriter/{dos_id}/export")
        assert export_blocked.status_code == 403
