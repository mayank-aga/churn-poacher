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
    company_description: Optional[str] = None
    estimated_size: str = "50-250 employees"
    industry: Optional[str] = None
    tech_stack: Dict[str, Any] = Field(default_factory=dict)
    infrastructure_indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Explicit Separate Qualification Dimensions
    icp_score: float = Field(default=0.0, ge=0.0, le=1.0)
    identity_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    technology_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    qualification_status: str = Field(default="REVIEW_REQUIRED", description="ACCEPTED, REVIEW_REQUIRED, REJECTED")
    
    decision_makers: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_sources: List[str] = Field(default_factory=list)
    evidence_records: List[Dict[str, Any]] = Field(default_factory=list)
    is_synthetic: bool = False
    last_enriched_at: Optional[datetime] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    company_description: Optional[str] = None
    estimated_size: Optional[str] = None
    industry: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = None
    infrastructure_indicators: Optional[Dict[str, Any]] = None
    icp_score: Optional[float] = None
    identity_confidence: Optional[float] = None
    technology_confidence: Optional[float] = None
    qualification_status: Optional[str] = None
    decision_makers: Optional[List[Dict[str, Any]]] = None
    evidence_sources: Optional[List[str]] = None
    evidence_records: Optional[List[Dict[str, Any]]] = None
    last_enriched_at: Optional[datetime] = None


class CompanyRead(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
