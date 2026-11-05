"""
Pipeline and Integration Tests for Central Orchestrator.
Tests end-to-end execution, qualification gate routing, partial resumption,
duplicate prevention, and retry exhaustion.
"""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.signal import Signal
from app.models.company import Company
from app.models.dossier import DepositionDossier
from app.models.workflow import WorkflowExecution
from app.agents.orchestrator.state_machine import WorkflowState, WorkflowStep
from app.agents.orchestrator.schemas import WorkflowRunRequest
from app.agents.orchestrator.orchestrator import CentralOrchestrator
from app.agents.orchestrator.pipeline import PipelineRunner


@pytest.mark.asyncio
async def test_orchestrator_pipeline_end_to_end_success():
    async with AsyncSessionLocal() as db:
        # 1. Create a qualified enterprise signal
        sig_id = f"test-sig-{uuid.uuid4().hex[:8]}"
        signal = Signal(
            signal_id=sig_id,
            source="REDDIT",
            original_url="https://reddit.com/r/devops/comments/datadog_bill",
            vendor="Datadog",
            complaint_category="PRICING_SHOCK",
            raw_content="Our team at CloudScale Logistics (cloudscale.io) is seeing our Datadog APM bill skyrocket 45% on 150 Kubernetes nodes.",
            urgency_score=0.88,
            extracted_evidence={"inferred_nodes": 150, "company_name": "CloudScale Logistics", "domain": "cloudscale.io"},
            is_synthetic=True,
            status="NEW",
        )
        db.add(signal)
        await db.commit()
        await db.refresh(signal)

        # 2. Run Pipeline
        req = WorkflowRunRequest(
            signal_id=signal.id,
            target_challenger="SigNoz Cloud",
            include_synthetic=True,
            timeout_seconds=30,
        )
        workflow = await CentralOrchestrator.run_pipeline(request=req, db=db)

        # 3. Assertions
        assert workflow.status == WorkflowState.DRAFT_PENDING_APPROVAL.value
        assert workflow.current_step == WorkflowStep.APPROVAL_GATE.value
        assert workflow.company_id is not None
        assert workflow.dossier_id is not None
        assert len(workflow.step_history) >= 4  # PROFILER, QUALIFICATION, FINOPS, ARCHITECT, COPYWRITER

        # Check DepositionDossier
        dossier_res = await db.execute(select(DepositionDossier).where(DepositionDossier.id == workflow.dossier_id))
        dossier = dossier_res.scalar_one_or_none()
        assert dossier is not None
        assert dossier.financial_delta is not None
        assert dossier.migration_blueprint is not None
        assert dossier.outreach_drafts is not None
        assert dossier.status == "DRAFT_PENDING_APPROVAL"


@pytest.mark.asyncio
async def test_orchestrator_qualification_gate_rejects_unqualified():
    async with AsyncSessionLocal() as db:
        # Create an unqualified signal (hobbyist / student)
        sig_id = f"test-sig-hobby-{uuid.uuid4().hex[:8]}"
        signal = Signal(
            signal_id=sig_id,
            source="HACKER_NEWS",
            original_url="https://news.ycombinator.com/item?id=888",
            vendor="Datadog",
            complaint_category="GENERAL_DISCUSSION",
            raw_content="I am a student working on a hobby homework project and Datadog trial ended.",
            urgency_score=0.20,
            extracted_evidence={"inferred_nodes": 1},
            is_synthetic=True,
            status="NEW",
        )
        db.add(signal)
        await db.commit()
        await db.refresh(signal)

        # Run Pipeline
        req = WorkflowRunRequest(
            signal_id=signal.id,
            target_challenger="SigNoz Cloud",
            include_synthetic=True,
        )
        workflow = await CentralOrchestrator.run_pipeline(request=req, db=db)

        # The orchestrator MUST either reject during Profiling (anonymous/hobbyist) or at the Qualification Gate
        assert workflow.status == WorkflowState.REJECTED.value
        assert workflow.dossier_id is None  # Downstream FinOps/Dossier generation was NOT run!

        # Check step history contains either UNRESOLVED or DISQUALIFIED
        statuses = [s["status"] for s in workflow.step_history]
        assert "DISQUALIFIED" in statuses or "UNRESOLVED" in statuses


@pytest.mark.asyncio
async def test_orchestrator_partial_resumption():
    async with AsyncSessionLocal() as db:
        # Create Signal and Company already verified
        sig_id = f"test-sig-{uuid.uuid4().hex[:8]}"
        signal = Signal(
            signal_id=sig_id,
            source="REDDIT",
            original_url="https://acme.io/blog",
            complaint_category="PRICING_SHOCK",
            raw_content="Acme Corp Datadog spend is high.",
            urgency_score=0.85,
            is_synthetic=True,
            status="QUALIFIED",
        )
        db.add(signal)
        await db.flush()

        company = Company(
            signal_id=signal.id,
            name="Acme Corp",
            domain="acme.io",
            industry="Software",
            estimated_size="100-500 employees",
            icp_score=0.85,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db.add(company)
        await db.commit()

        # Create workflow simulating failure after FINOPS
        workflow = WorkflowExecution(
            workflow_type="SINGLE_COMPANY",
            status=WorkflowState.FAILED.value,
            current_step="ARCHITECT",
            signal_id=signal.id,
            company_id=company.id,
            target_challenger="SigNoz Cloud",
            max_retries=3,
            retry_count=1,
            step_history=[
                {"step_name": WorkflowStep.PROFILER.value, "status": "SUCCESS", "started_at": "", "completed_at": "", "duration_ms": 100, "details": {}},
                {"step_name": WorkflowStep.QUALIFICATION.value, "status": "SUCCESS", "started_at": "", "completed_at": "", "duration_ms": 50, "details": {}},
                {"step_name": WorkflowStep.FINOPS.value, "status": "SUCCESS", "started_at": "", "completed_at": "", "duration_ms": 120, "details": {}},
                {"step_name": WorkflowStep.ARCHITECT.value, "status": "FAILED", "started_at": "", "completed_at": "", "duration_ms": 0, "details": {}, "error_message": "Transient network glitch"},
            ],
            input_payload={"company_id": company.id, "target_challenger": "SigNoz Cloud"},
            output_payload={},
            is_synthetic=True,
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)

        # Trigger Retry
        resumed_wf = await CentralOrchestrator.retry_workflow(workflow_id=workflow.id, db=db)

        # Assert workflow succeeded without re-running Profiler, Qualification, or FinOps
        assert resumed_wf.status == WorkflowState.DRAFT_PENDING_APPROVAL.value
        assert resumed_wf.dossier_id is not None
        step_names = [s["step_name"] for s in resumed_wf.step_history if s["status"] == "SUCCESS"]
        assert WorkflowStep.ARCHITECT.value in step_names
        assert WorkflowStep.COPYWRITER.value in step_names


@pytest.mark.asyncio
async def test_orchestrator_duplicate_prevention():
    async with AsyncSessionLocal() as db:
        # Create an active in-flight workflow
        company_id = str(uuid.uuid4())
        active_wf = WorkflowExecution(
            workflow_type="SINGLE_COMPANY",
            status=WorkflowState.FINOPS_RUNNING.value,
            current_step="FINOPS",
            company_id=company_id,
            target_challenger="SigNoz Cloud",
            max_retries=3,
            is_synthetic=True,
        )
        db.add(active_wf)
        await db.commit()

        # Attempt to run another workflow on the same company while active_wf is running
        req = WorkflowRunRequest(
            company_id=company_id,
            target_challenger="SigNoz Cloud",
        )
        with pytest.raises(ValueError, match="already in progress"):
            await CentralOrchestrator.run_pipeline(request=req, db=db)


@pytest.mark.asyncio
async def test_orchestrator_retry_exhaustion():
    async with AsyncSessionLocal() as db:
        # Create workflow that exhausted all retries
        failed_wf = WorkflowExecution(
            workflow_type="FULL_PIPELINE",
            status=WorkflowState.FAILED.value,
            current_step="FINOPS",
            retry_count=3,
            max_retries=3,
            error_details="Permanent failure",
            is_synthetic=True,
        )
        db.add(failed_wf)
        await db.commit()

        # Attempting retry without override must fail
        with pytest.raises(ValueError, match="exhausted its retry limit"):
            await CentralOrchestrator.retry_workflow(workflow_id=failed_wf.id, db=db)


@pytest.mark.asyncio
async def test_orchestrator_concurrent_distinct_workflows():
    import asyncio
    async with AsyncSessionLocal() as db1, AsyncSessionLocal() as db2:
        # Create signals
        sig1 = Signal(
            signal_id=f"test-sig-c1-{uuid.uuid4().hex[:6]}",
            source="REDDIT",
            original_url="https://alpha.com",
            complaint_category="PRICING_SHOCK",
            raw_content="Alpha telemetry costs",
            is_synthetic=True,
        )
        sig2 = Signal(
            signal_id=f"test-sig-c2-{uuid.uuid4().hex[:6]}",
            source="REDDIT",
            original_url="https://beta.com",
            complaint_category="OUTAGE",
            raw_content="Beta telemetry outage",
            is_synthetic=True,
        )
        db1.add(sig1)
        db1.add(sig2)
        await db1.flush()

        # Create two distinct companies
        comp1 = Company(
            signal_id=sig1.id,
            name="Concurrent Alpha",
            domain="concurrentalpha.com",
            estimated_size="100-250 employees",
            icp_score=0.85,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        comp2 = Company(
            signal_id=sig2.id,
            name="Concurrent Beta",
            domain="concurrentbeta.com",
            estimated_size="250-500 employees",
            icp_score=0.88,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db1.add(comp1)
        db1.add(comp2)
        await db1.commit()
        await db1.refresh(comp1)
        await db1.refresh(comp2)

        req1 = WorkflowRunRequest(company_id=comp1.id, target_challenger="SigNoz Cloud")
        req2 = WorkflowRunRequest(company_id=comp2.id, target_challenger="Grafana Cloud")

        # Execute concurrently
        wf1, wf2 = await asyncio.gather(
            CentralOrchestrator.run_pipeline(request=req1, db=db1),
            CentralOrchestrator.run_pipeline(request=req2, db=db2),
        )

        assert wf1.status == WorkflowState.DRAFT_PENDING_APPROVAL.value
        assert wf2.status == WorkflowState.DRAFT_PENDING_APPROVAL.value
        assert wf1.dossier_id is not None
        assert wf2.dossier_id is not None
        assert wf1.dossier_id != wf2.dossier_id
