"""
Pydantic Schemas for Agent Execution Logs.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ExecutionLogCreate(BaseModel):
    agent_name: str
    signal_id: Optional[str] = None
    status: str
    execution_time_ms: int = 0
    input_payload: Dict[str, Any] = {}
    output_payload: Dict[str, Any] = {}
    error_message: Optional[str] = None


class ExecutionLogRead(ExecutionLogCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
