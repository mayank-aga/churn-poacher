"""
Pydantic Schemas for Companies.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class CompanyBase(BaseModel):
    signal_id: str
    name: str
    domain: Optional[str] = None
    estimated_size: str = "50-250 employees"
    industry: Optional[str] = None
    tech_stack: Dict[str, Any] = Field(default_factory=dict)
    infrastructure_indicators: Dict[str, Any] = Field(default_factory=dict)
    icp_score: float = Field(default=0.0, ge=0.0, le=1.0)
    identity_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    decision_makers: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_sources: List[str] = Field(default_factory=list)
    is_synthetic: bool = False


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    estimated_size: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = None
    infrastructure_indicators: Optional[Dict[str, Any]] = None
    icp_score: Optional[float] = None
    identity_confidence: Optional[float] = None
    decision_makers: Optional[List[Dict[str, Any]]] = None
    evidence_sources: Optional[List[str]] = None


class CompanyRead(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
