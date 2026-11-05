"""
Pydantic Schemas for Signals.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SignalBase(BaseModel):
    signal_id: str
    source: str = Field(..., description="REDDIT, HACKER_NEWS, TWITTER, DATADOG_STATUS, SYNTHETIC")
    original_url: str
    author_handle: Optional[str] = None
    vendor: str = "Datadog"
    complaint_category: str = Field(..., description="PRICING_SHOCK, OUTAGE, DEPRECATION, RELIABILITY")
    raw_content: str
    sentiment: str = "NEGATIVE"
    urgency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    extracted_evidence: Dict[str, Any] = Field(default_factory=dict)
    is_synthetic: bool = False
    status: str = "NEW"


class SignalCreate(SignalBase):
    pass


class SignalUpdate(BaseModel):
    complaint_category: Optional[str] = None
    sentiment: Optional[str] = None
    urgency_score: Optional[float] = None
    extracted_evidence: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class SignalRead(SignalBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
