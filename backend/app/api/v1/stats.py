"""
API Endpoints for Dashboard Overview Statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.signal import Signal
from app.models.company import Company
from app.models.dossier import DepositionDossier
from app.schemas.stats import DashboardStats

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/overview", response_model=DashboardStats)
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    # 1. Total Signals
    signals_count_res = await db.execute(select(func.count(Signal.id)))
    signals_count = signals_count_res.scalar() or 0

    # 2. Total Companies
    companies_count_res = await db.execute(select(func.count(Company.id)))
    companies_count = companies_count_res.scalar() or 0

    # 3. Qualified Prospects (ICP Score >= 0.7)
    qualified_count_res = await db.execute(
        select(func.count(Company.id)).where(Company.icp_score >= 0.7)
    )
    qualified_count = qualified_count_res.scalar() or 0

    # 4. Total Potential Annual Savings across dossiers
    dossiers_res = await db.execute(select(DepositionDossier.financial_delta))
    dossier_deltas = dossiers_res.scalars().all()
    
    total_savings = 0.0
    for delta in dossier_deltas:
        if isinstance(delta, dict):
            total_savings += float(delta.get("estimated_annual_savings", 0.0))

    return DashboardStats(
        signals_detected=signals_count,
        companies_identified=companies_count,
        qualified_prospects=qualified_count,
        total_potential_annual_savings=total_savings,
        agent_status={
            "listener": "idle",
            "profiler": "idle",
            "finops_architect": "idle",
            "copywriter": "idle",
            "orchestrator": "idle",
        }
    )
