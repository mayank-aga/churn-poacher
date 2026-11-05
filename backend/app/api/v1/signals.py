"""
API Endpoints for Signals.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.signal import Signal
from app.schemas.signal import SignalCreate, SignalRead

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.get("", response_model=List[SignalRead])
async def list_signals(
    source: Optional[str] = Query(None, description="Filter by source (REDDIT, HACKER_NEWS, etc.)"),
    vendor: Optional[str] = Query(None, description="Filter by vendor"),
    complaint_category: Optional[str] = Query(None, description="Filter by complaint category (PRICING_SHOCK, OUTAGE, etc.)"),
    min_urgency: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum urgency score"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Signal).order_by(desc(Signal.created_at)).limit(limit)
    if source:
        query = query.where(Signal.source == source)
    if vendor:
        query = query.where(Signal.vendor == vendor)
    if complaint_category:
        query = query.where(Signal.complaint_category == complaint_category)
    if min_urgency is not None:
        query = query.where(Signal.urgency_score >= min_urgency)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=SignalRead, status_code=201)
async def create_signal(
    payload: SignalCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check for duplicate signal_id
    existing = await db.execute(select(Signal).where(Signal.signal_id == payload.signal_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Signal with ID '{payload.signal_id}' already exists")

    signal = Signal(**payload.model_dump())
    db.add(signal)
    await db.flush()
    await db.refresh(signal)
    return signal


@router.get("/{signal_id}", response_model=SignalRead)
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
):
    query = select(Signal).where((Signal.id == signal_id) | (Signal.signal_id == signal_id))
    result = await db.execute(query)
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal
