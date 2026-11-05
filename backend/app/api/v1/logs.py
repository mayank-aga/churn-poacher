"""
API Endpoints for Agent Execution Logs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.execution_log import AgentExecutionLog
from app.schemas.execution_log import ExecutionLogCreate, ExecutionLogRead

router = APIRouter(prefix="/logs", tags=["Agent Logs"])


@router.get("", response_model=List[ExecutionLogRead])
async def list_logs(
    agent_name: Optional[str] = Query(None, description="Filter by agent"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS, FAILED, etc.)"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(AgentExecutionLog).order_by(desc(AgentExecutionLog.created_at)).limit(limit)
    if agent_name:
        query = query.where(AgentExecutionLog.agent_name == agent_name)
    if status:
        query = query.where(AgentExecutionLog.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ExecutionLogRead, status_code=201)
async def create_log(
    payload: ExecutionLogCreate,
    db: AsyncSession = Depends(get_db),
):
    log_entry = AgentExecutionLog(**payload.model_dump())
    db.add(log_entry)
    await db.flush()
    await db.refresh(log_entry)
    return log_entry
