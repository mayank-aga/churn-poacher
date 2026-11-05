"""
Company ORM Model.
Stores verified entity profiling, infrastructure footprints, technology stacks,
evidence audits, and ICP qualification scores.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Float, Boolean, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.signal import Signal
    from app.models.dossier import DepositionDossier


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id: Mapped[str] = mapped_column(String(36), ForeignKey("signals.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(200), index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    company_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_size: Mapped[str] = mapped_column(String(100), default="50-250 employees")
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Technology and Infrastructure Footprints
    tech_stack: Mapped[dict] = mapped_column(JSON, default=dict)
    infrastructure_indicators: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Qualification Metrics (Separate Dimensions)
    icp_score: Mapped[float] = mapped_column(Float, default=0.0)
    identity_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    technology_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Qualification State: ACCEPTED, REVIEW_REQUIRED, REJECTED
    qualification_status: Mapped[str] = mapped_column(
        String(50), default="REVIEW_REQUIRED", index=True
    )
    
    # Relevant verified/inferred decision maker titles (e.g., VP of DevOps, CTO)
    decision_makers: Mapped[list] = mapped_column(JSON, default=list)
    
    # Publicly verifiable sources & citations
    evidence_sources: Mapped[list] = mapped_column(JSON, default=list)
    evidence_records: Mapped[list] = mapped_column(JSON, default=list)
    
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    last_enriched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    signal: Mapped["Signal"] = relationship("Signal", back_populates="companies")
    dossiers: Mapped[List["DepositionDossier"]] = relationship("DepositionDossier", back_populates="company", cascade="all, delete-orphan")
