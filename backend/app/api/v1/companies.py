"""
API Endpoints for Companies.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=List[CompanyRead])
async def list_companies(
    qualification_status: Optional[str] = Query(None, description="Filter by qualification status (ACCEPTED, REJECTED, REVIEW_REQUIRED)"),
    min_icp_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Company).order_by(desc(Company.created_at)).limit(limit)
    if qualification_status:
        query = query.where(Company.qualification_status == qualification_status)
    if min_icp_score is not None:
        query = query.where(Company.icp_score >= min_icp_score)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CompanyRead, status_code=201)
async def create_company(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    company = Company(**payload.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
