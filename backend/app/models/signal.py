"""
Signal ORM Model.
Stores raw and classified competitive distress signals from Reddit, HN, Twitter, and status pages.
"""

import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.dossier import DepositionDossier


class Signal(Base, TimestampMixin):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)  # REDDIT, HACKER_NEWS, TWITTER, DATADOG_STATUS, SYNTHETIC
    original_url: Mapped[str] = mapped_column(String(500))
    author_handle: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    vendor: Mapped[str] = mapped_column(String(100), default="Datadog", index=True)
    complaint_category: Mapped[str] = mapped_column(String(100), index=True)  # PRICING_SHOCK, OUTAGE, DEPRECATION, RELIABILITY
    raw_content: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(50), default="NEGATIVE")
    urgency_score: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Structured evidence (e.g., quotes, numbers, timestamps)
    extracted_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Explicit labelling for synthetic/demo signals
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="NEW", index=True)  # NEW, PROFILED, QUALIFIED, REJECTED, ARCHIVED

    # Relationships
    companies: Mapped[List["Company"]] = relationship("Company", back_populates="signal", cascade="all, delete-orphan")
    dossiers: Mapped[List["DepositionDossier"]] = relationship("DepositionDossier", back_populates="signal", cascade="all, delete-orphan")
