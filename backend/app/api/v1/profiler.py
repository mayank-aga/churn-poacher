"""
Profiler Agent API Endpoints.
Provides manual profiling triggers, company intelligence retrieval, and qualification metrics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.session import get_db
from app.models.company import Company
from app.models.signal import Signal
from app.schemas.company import CompanyRead
from app.agents.profiler.agent import ProfilerAgent
from app.agents.profiler.schemas import (
    ProfilerExecutionSummary,
    ProfilerStatusReport,
    ProfilerMetricsReport,
)

router = APIRouter(prefix="/profiler", tags=["Profiler Agent"])
profiler_agent = ProfilerAgent()


class RunProfilerRequest(BaseModel):
    max_signals: int = 20


@router.post("/run", response_model=ProfilerExecutionSummary)
async def trigger_profiler_run(
    request: Optional[RunProfilerRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """Triggers entity resolution, technology profiling, and ICP qualification on new signals."""
    limit = request.max_signals if request else 20
    return await profiler_agent.run_profiling_cycle(db=db, max_signals=limit)


@router.get("/status", response_model=ProfilerStatusReport)
async def get_profiler_status(
    db: AsyncSession = Depends(get_db),
):
    """Returns operational status and pending signal counts for the Profiler Agent."""
    return await profiler_agent.get_status_report(db)


@router.get("/companies", response_model=List[CompanyRead])
async def list_profiled_companies(
    status: Optional[str] = Query(None, description="ACCEPTED, REVIEW_REQUIRED, REJECTED"),
    min_icp_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lists enriched companies with optional qualification state or ICP score filter."""
    query = select(Company).order_by(desc(Company.created_at)).limit(limit)
    if status:
        query = query.where(Company.qualification_status == status.upper())
    if min_icp_score is not None:
        query = query.where(Company.icp_score >= min_icp_score)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/companies/{company_id}", response_model=CompanyRead)
async def get_company_intelligence(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Returns the complete verified company intelligence dossier."""
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return company


@router.get("/metrics", response_model=ProfilerMetricsReport)
async def get_profiler_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Aggregates quantitative qualification metrics across all profiled entities."""
    # Total signals processed / unresolved
    unresolved_res = await db.execute(
        select(func.count(Signal.id)).where(Signal.status == "UNRESOLVED")
    )
    unresolved_count = unresolved_res.scalar() or 0

    profiled_res = await db.execute(
        select(func.count(Signal.id)).where(Signal.status.in_(["PROFILED", "QUALIFIED", "UNRESOLVED"]))
    )
    signals_processed = profiled_res.scalar() or 0

    # Total companies identified
    comp_count_res = await db.execute(select(func.count(Company.id)))
    companies_identified = comp_count_res.scalar() or 0

    # Counts by qualification status
    accepted_res = await db.execute(
        select(func.count(Company.id)).where(Company.qualification_status == "ACCEPTED")
    )
    accepted_count = accepted_res.scalar() or 0

    review_res = await db.execute(
        select(func.count(Company.id)).where(Company.qualification_status == "REVIEW_REQUIRED")
    )
    review_count = review_res.scalar() or 0

    rejected_res = await db.execute(
        select(func.count(Company.id)).where(Company.qualification_status == "REJECTED")
    )
    rejected_count = rejected_res.scalar() or 0

    # Averages
    avg_res = await db.execute(
        select(
            func.avg(Company.icp_score),
            func.avg(Company.identity_confidence),
            func.avg(Company.technology_confidence),
        )
    )
    avg_icp, avg_id, avg_tech = avg_res.one()

    return ProfilerMetricsReport(
        signals_processed=signals_processed,
        companies_identified=companies_identified,
        companies_accepted=accepted_count,
        companies_requiring_review=review_count,
        companies_rejected=rejected_count,
        unresolved_signals=unresolved_count,
        average_icp_score=round(float(avg_icp or 0.0), 2),
        average_identity_confidence=round(float(avg_id or 0.0), 2),
        average_technology_confidence=round(float(avg_tech or 0.0), 2),
    )
