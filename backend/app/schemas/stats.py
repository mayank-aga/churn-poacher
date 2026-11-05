"""
Pydantic Schemas for Dashboard Overview Statistics.
"""

from typing import Dict, Any
from pydantic import BaseModel


class DashboardStats(BaseModel):
    signals_detected: int = 0
    companies_identified: int = 0
    qualified_prospects: int = 0
    total_potential_annual_savings: float = 0.0
    agent_status: Dict[str, str] = {
        "listener": "idle",
        "profiler": "idle",
        "finops_architect": "idle",
        "copywriter": "idle",
        "orchestrator": "idle",
    }
