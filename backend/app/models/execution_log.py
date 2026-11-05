"""
Agent Execution Log ORM Model.
Tracks execution states, latencies, payloads, and retries across the multi-agent pipeline.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AgentExecutionLog(Base, TimestampMixin):
    __tablename__ = "agent_execution_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name: Mapped[str] = mapped_column(String(50), index=True)  # LISTENER, PROFILER, FINOPS_ARCHITECT, COPYWRITER, ORCHESTRATOR
    signal_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)  # STARTED, SUCCESS, FAILED, RETRYING
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
