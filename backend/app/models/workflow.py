"""
Workflow Execution ORM Model for Central Orchestrator.
Tracks state machine transitions, step execution histories, retry counts, and errors.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Boolean, JSON, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class WorkflowExecution(Base, TimestampMixin):
    __tablename__ = "workflow_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_type: Mapped[str] = mapped_column(String(50), default="FULL_PIPELINE", index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    current_step: Mapped[str] = mapped_column(String(50), default="INIT", index=True)
    
    signal_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    company_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    dossier_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    target_challenger: Mapped[str] = mapped_column(String(100), default="SigNoz Cloud")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    execution_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    # Detailed log of step transitions: [{"step": str, "status": str, "started_at": str, "completed_at": str, "duration_ms": int, "details": dict}]
    step_history: Mapped[list] = mapped_column(JSON, default=list)
    
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
