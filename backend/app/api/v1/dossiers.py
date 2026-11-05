"""
API Endpoints for Deposition Dossiers.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.dossier import DepositionDossier
from app.schemas.dossier import DossierCreate, DossierRead, DossierStatusUpdate

router = APIRouter(prefix="/dossiers", tags=["Deposition Dossiers"])


@router.get("", response_model=List[DossierRead])
async def list_dossiers(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    status: Optional[str] = Query(None, description="Filter by status: DRAFT_PENDING_APPROVAL, APPROVED, etc."),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(DepositionDossier).order_by(desc(DepositionDossier.created_at)).limit(limit)
    if company_id:
        query = query.where(DepositionDossier.company_id == company_id)
    if status:
        query = query.where(DepositionDossier.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=DossierRead, status_code=201)
async def create_dossier(
    payload: DossierCreate,
    db: AsyncSession = Depends(get_db),
):
    dossier = DepositionDossier(**payload.model_dump())
    db.add(dossier)
    await db.flush()
    await db.refresh(dossier)
    return dossier


@router.get("/{dossier_id}", response_model=DossierRead)
async def get_dossier(
    dossier_id: str,
    db: AsyncSession = Depends(get_db),
):
    query = select(DepositionDossier).where(DepositionDossier.id == dossier_id)
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return dossier


@router.patch("/{dossier_id}/status", response_model=DossierRead)
async def update_dossier_status(
    dossier_id: str,
    payload: DossierStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    valid_statuses = {"DRAFT_PENDING_APPROVAL", "APPROVED", "REJECTED", "SENT"}
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of: {valid_statuses}"
        )
    
    query = select(DepositionDossier).where(DepositionDossier.id == dossier_id)
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    
    dossier.status = payload.status
    await db.flush()
    await db.refresh(dossier)
    return dossier
